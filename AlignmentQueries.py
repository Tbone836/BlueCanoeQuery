import boto3
import time
import json
import datetime
from masterBackwardsSearch import goBackToInfo
from GetListOfLogRecords import getListOfUniquePTR
from queryWaiter import queryWaitResults

client = boto3.client("logs")
startM = int(input("Start Month? "))
startD = int(input("Start Day? "))
startY = int(input("Start Year? "))

endM = int(input("End Month? "))
endD = int(input("End Day? "))
endY = int(input("End Year? "))

response = client.start_query(
    logGroupName = '/aws/lambda/ml-coordinator',
    queryString= "filter (data = 'invokeLambda(ml-word-phoneme-alignment): Lambda failed - PocketSphinx met trouble to match final result with the grammar in some frames on the word-level alignment')", 
    #queryString = "filter (data = 'invokeLambda(ml-lr_classifier): Lambda failed - undefined')",
    #queryString = "filter (data = 'invokeLambda(ml-vowel-quality): Lambda failed - undefined')",
    #queryString = "filter (data = 'invokeLambda(ml-vowel-insertion): Lambda failed - Error In Processing At Least One phonemeTimingInfo')",
    #These are the time stamps representing the last week.
    startTime= int(datetime.datetime(startY, startM, startD, 0, 0).timestamp()),
    endTime=int(datetime.datetime(endY, endM, endD, 0, 0).timestamp())
)

#This makes the program wait until the query has completed. Then it returns all of the results that satisfy the query
results = queryWaitResults(client, response)

#The results contains the message (Json converted to a string) and the ptr
#The ptr is a value that points to the log group, log stream, and timestamp of the query results
ptrRecords = getListOfUniquePTR(results)

print(len(ptrRecords))

i=0

for ptr in ptrRecords:
    #This function returns a dictionary with the time the log was made and the stream and logGroupName
    ptrResponse = client.get_log_record(logRecordPointer = ptr)
    events = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName=ptrResponse['logRecord']['@logStream'],
                                startTime=int(ptrResponse['logRecord']['@timestamp']),
                                #The actual time could be rounded up or down so I have the +1 to account for it
                                endTime=int(ptrResponse['logRecord']['@timestamp'])+1,
                                limit = 1, startFromHead = True)

    notFormattedData = goBackToInfo(ptrResponse['logRecord']['@logStream'], events['nextBackwardToken'],
                                             "invokeLambda(ml-word-phoneme-alignment): sending request", "transcript")

    #Since the nested dictionary is converted into a string, I split it at the "" marks to index the words I wanted
    #And then added them to a new dictionary
    notFormattedData = notFormattedData.split('\"')

    #This gets the split list of everything after the word "transcript"
    transcriptWords = notFormattedData[-1*(len(notFormattedData)-notFormattedData.index('transcript')-1):]
    
    #This is the new dictionary
    dictJson = {}

    #It is always "L1" : "language"  ->  [..., 'L1', ':', 'language',... ] so language is two after L1
    dictJson['L1'] = notFormattedData[notFormattedData.index('L1')+2]
    dictJson['b64Audio'] = notFormattedData[notFormattedData.index('b64Audio')+2]
    transcriptArray = []
    transcriptDict={}

    for x in range(0, len(transcriptWords)):
        currentWord = transcriptWords[x]
        #The spliced array is like ['[{', 'word', ':', 'red', '},{' , 'isFocusWord' , ':false}]']
        if currentWord == 'word':
            transcriptDict['word'] = transcriptWords[x+2]
        elif currentWord == 'isFocusWord':
            if transcriptWords[x+1][1] == 't':
                #This pulls the word true from the string ':true}]'
                transcriptDict['isFocusWord'] = transcriptWords[x+1][1:5]
            else:
                #This pulls the word false from the string ':false}]'
                transcriptDict['isFocusWord'] = transcriptWords[x+1][1:6]
            transcriptArray.append(transcriptDict)
            transcriptDict = {}

    dictJson['requestID'] = events['ResponseMetadata']['RequestId']
    dictJson['transcript'] = transcriptArray

    with open("alignment" + str(i) + ".json","w") as outfile:
        #converts the new dictionary to a json file and writes it to a new file
        json.dump(dictJson, outfile, indent = 4, sort_keys = True)
    i += 1