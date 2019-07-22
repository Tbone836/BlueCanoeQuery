import boto3
import time
import json
import datetime
from LRBackwardsSearch import goBackToInfo

client = boto3.client("logs")
startM = int(input("Start Month? "))
startD = int(input("Start Day? "))
startY = int(input("Start Year? "))

endM = int(input("End Month? "))
endD = int(input("End Day? "))
endY = int(input("End Year? "))

response = client.start_query(
    logGroupName = '/aws/lambda/ml-coordinator',
    #queryString= "filter (data = 'invokeLambda(ml-word-phoneme-alignment): Lambda failed - PocketSphinx met trouble to match final result with the grammar in some frames on the word-level alignment')", 
    queryString = "filter (data = 'invokeLambda(ml-lr_classifier): Lambda failed - undefined')",
    #queryString = "filter (data = 'invokeLambda(ml-vowel-quality): Lambda failed - undefined')",
    #queryString = "filter (data = 'invokeLambda(ml-vowel-insertion): Lambda failed - Error In Processing At Least One phonemeTimingInfo')",
    #These are the time stamps representing the last week.
    startTime= int(datetime.datetime(startY, startM, startD, 0, 0).timestamp()),
    endTime=int(datetime.datetime(endY, endM, endD, 0, 0).timestamp())
)
status = client.get_query_results(queryId = response['queryId'])['status']
#Keeps the query running until it is complete
count = 0
while(status != 'Complete'):
    time.sleep(1)
    status = client.get_query_results(queryId = response['queryId'])['status']
    print(str(count) + status)
    count += 1
results = client.get_query_results(queryId = response['queryId'])

logsWithErrors = []
ptrRecords = []
for i in range(0, len(results['results'])):
    #Every set of log events has a start and end log. Every log in that set has a similar identifier
    #This will help to avoid duplicates
    identifier = results['results'][i][1]['value'][25:60]
    #This gets the ptr value which tells us the record of the log entry
    ptr = results['results'][i][2]['value']
    #Checks to make sure there is no log from the same set (they would point to the same information)
    if identifier not in logsWithErrors:
        logsWithErrors.append(identifier)
        ptrRecords.append(ptr)
print(len(ptrRecords))
i=0
for ptr in ptrRecords:
    #This function returns a dictionary with the time the log was made and the stream and logGroupName
    response = client.get_log_record(logRecordPointer = ptr)
    events = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName=response['logRecord']['@logStream'],
                                startTime=int(response['logRecord']['@timestamp']),
                                #The actual time could be rounded up or down so I have the +1 to account for it
                                endTime=int(response['logRecord']['@timestamp'])+1,
                                limit = 1, startFromHead = True)

    notFormattedData = goBackToInfo(response['logRecord']['@logStream'], events['nextBackwardToken'])
    notFormattedData = notFormattedData.split('\"')

    transcriptWords = notFormattedData[-1*(len(notFormattedData)-notFormattedData.index('expectedPhonemes')-1):]
  
    dictJson = {}
    dictJson['L1'] = notFormattedData[notFormattedData.index('L1')+2]
    dictJson['b64Audio'] = notFormattedData[notFormattedData.index('b64Audio')+2]
    transcriptArray = []
    transcriptDict={}
    transcriptDictRev={}
    print(transcriptWords)
    for x in range(0, len(transcriptWords)):
        currentWord = transcriptWords[x]
        #The spliced array is like ['[{', 'word', ':', 'red', '},{' , 'isFocusWord , :false}]]
        #It repeats itself every six indexes so the 3 is the distance the value of 'word' from a mod 6
        if currentWord == 'startTime':
            transcriptDict['startTime'] = transcriptWords[x+1][1:-1]
        elif currentWord == 'endTime':
            transcriptDict['endTime'] = transcriptWords[x+1][1:-1]
        elif currentWord == 'phoneme':
            transcriptDict['phoneme'] = transcriptWords[x+1]
            #transcriptDictRev['phoneme'] = transcriptDict['phoneme']
            #transcriptDictRev['endTime'] = transcriptDict['endTime']
            #transcriptDictRev['startTime'] = transcriptDict['startTime']
            #transcriptArray.append(transcriptDictRev)
            #transcriptDict = {}
            transcriptDictRev={}
    dictJson['requestID'] = events['ResponseMetadata']['RequestId']
    dictJson['transcript'] = transcriptArray
    with open("lrErrors" + str(i) + ".json","w") as outfile:
        json.dump(dictJson, outfile, indent = 4, sort_keys = True)
    i+=1
