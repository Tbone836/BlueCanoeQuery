import boto3
import time
import json
import datetime
from UpdateBackwardsSearch import goBackToInfo

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
    #queryString = "filter (response.succeeded = FALSE)",
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
#print(results['results'][0])

logsWithErrors = []
ptrRecords = []
for i in range(0, len(results['results'])):
    #This gets the ptr value which tells us the record of the log entry

    identifier = results['results'][i][1]['value'][25:60]
    ptr = results['results'][i][2]['value']
    if identifier not in logsWithErrors:
        logsWithErrors.append(identifier)
        ptrRecords.append(ptr)
print(len(ptrRecords))
i=0
for ptr in ptrRecords:
    response = client.get_log_record(logRecordPointer = ptr)
    events = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName=response['logRecord']['@logStream'],
                                startTime=int(response['logRecord']['@timestamp']),
                                endTime=int(response['logRecord']['@timestamp'])+1,
                                limit = 1, startFromHead = True)

    formattedData = goBackToInfo(response['logRecord']['@logStream'], events['nextBackwardToken'])
    formattedData = formattedData.split('\"')
    transcriptWords = formattedData[-1*(len(formattedData)-formattedData.index('transcript')-1):]
    #print(len(transcriptWords))
    dictJson = {}
    dictJson['L1'] = formattedData[formattedData.index('L1')+2]
    dictJson['b64Audio'] = formattedData[formattedData.index('b64Audio')+2]
    transcriptArray = []
    transcriptDict={}
    for x in range(0, len(transcriptWords)):
        currentWord = transcriptWords[x]
        #print(str(x) + currentWord)
        if (x+3)%6 == 0:
            transcriptDict['word'] = currentWord
        elif (x%6==0 and x != 0):
            if currentWord[1] == 't':
                transcriptDict['isFocusWord'] = currentWord[1:5]
            else:
                transcriptDict['isFocusWord'] = currentWord[1:6]
            transcriptArray.append(transcriptDict)
            transcriptDict = {}
    dictJson['requestID'] = events['ResponseMetadata']['RequestId']
    dictJson['transcript'] = transcriptArray
    with open("testformat" + str(i) + ".json","w") as outfile:
        json.dump(dictJson, outfile, indent = 4, sort_keys = True)
    i+=1
