import boto3
import time
import json
import datetime
from masterBackwardsSearch import goBackToInfo
from ExpectedPhonemes import expectedPhonemesOrganize
from queryWaiter import queryWaitResults
from GetListOfLogRecords import getListOfUniquePTR

client = boto3.client("logs")

print("This program is to be used if the known error is supposed to contain 'expectedPhonemes'")

startM = int(input("Start Month? "))
startD = int(input("Start Day? "))
startY = int(input("Start Year? "))

endM = int(input("End Month? "))
endD = int(input("End Day? "))
endY = int(input("End Year? "))
print()
print("1: ml-lr_classifier")
print("2: ml-vowel-quality")
print("3: ml-vowel-insertion")
choice = int(input("Choose one of the errors: "))
prefix = input("What prefix for file names? ")

if choice == 1:
    errorChoice = "invokeLambda(ml-lr_classifier): Lambda failed - undefined"
    errorSearch = "invokeLambda(ml-lr_classifier): sending request"
elif choice == 2:
    errorChoice = "invokeLambda(ml-vowel-quality): Lambda failed - undefined"
    errorSearch = "invokeLambda(ml-vowel-quality): sending request"
elif choice == 3:
    errorChoice = "invokeLambda(ml-vowel-insertion): Lambda failed - Error In Processing At Least One phonemeTimingInfo"
    errorSearch = "invokeLambda(ml-vowel-insertion): sending request"

response = client.start_query(
    logGroupName = '/aws/lambda/ml-coordinator',
    #queryString= "filter (data = 'invokeLambda(ml-word-phoneme-alignment): Lambda failed - PocketSphinx met trouble to match final result with the grammar in some frames on the word-level alignment')", 
    queryString = "filter (data = '" + errorChoice + "')",
    #queryString = "filter (data = 'invokeLambda(ml-vowel-quality): Lambda failed - undefined')",
    #queryString = "filter (data = 'invokeLambda(ml-vowel-insertion): Lambda failed - Error In Processing At Least One phonemeTimingInfo')",
    #These are the time stamps representing the last week.
    startTime= int(datetime.datetime(startY, startM, startD, 0, 0).timestamp()),
    endTime=int(datetime.datetime(endY, endM, endD, 0, 0).timestamp())
)

results = queryWaitResults(client, response)

ptrRecords = getListOfUniquePTR(results)

print(len(ptrRecords))
i = 0

for ptr in ptrRecords:
    #This function returns a dictionary with the time the log was made and the stream and logGroupName
    response = client.get_log_record(logRecordPointer = ptr)
    events = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName=response['logRecord']['@logStream'],
                                startTime=int(response['logRecord']['@timestamp']),
                                #The actual time could be rounded up or down so I have the +1 to account for it
                                endTime=int(response['logRecord']['@timestamp'])+1,
                                limit = 1, startFromHead = True)

    notFormattedData = goBackToInfo(response['logRecord']['@logStream'], events['nextBackwardToken'],
                                    errorSearch, 'expectedPhonemes')
    if notFormattedData != None:
        dictJson = expectedPhonemesOrganize(notFormattedData, events)    
        with open(prefix + str(i) + ".json","w") as outfile:
            json.dump(dictJson, outfile, indent = 4, sort_keys = True)
        i += 1