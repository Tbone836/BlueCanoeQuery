import boto3
from BackwardsSearch import goBackToInfo
logs = 15
client = boto3.client('logs')
#Just a stream where there are succeeded = True values
trueStream = '2019/07/16/[175]e83d7c7098844adbaa1fe1085953ece0'
#Just a stream where there are succeeded = False values
falseStream = '2019/07/09/[175]55a61982812145f0b08635092661d9c5'#"2019/07/16/[175]9af35f5f1c8b4e65a9046013e2bc1db4"

#resp = client.filter_log_events(logGroupName='/aws/lambda/ml-coordinator')
#filters = client.describe_subscription_filters(logGroupName='/aws/lambda/ml-coordinator')
#This gets the first log event in the /aws/lambda/ml-coordinator stream

def pullDataString(events):
    #The events are converted to one big string, so I separate it into an array
    spliced = events[0]['message'].split("\"")

    dataIndex = None
    errorIndex = None
    for x in range(0, len(spliced)) :
        if spliced[x] == 'level':
            errorIndex = x
    if errorIndex != None:
        if spliced[errorIndex+2] == 'ERROR':
            print("This is the log event where we found the error.")
            print(spliced[0])
            return spliced[0]
        else:
            return None
streams = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName=falseStream,
                                limit = 1, startFromHead = True)

for x in range(0,logs):
    events = streams['events']
    errorEvent = pullDataString(events)
    if errorEvent != None:
        nativeLang, audio64 = goBackToInfo(falseStream, streams['nextBackwardToken'])
        break
    forwardToken = streams['nextForwardToken']
    streams = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                          logStreamName=falseStream,
                                          nextToken=forwardToken,
                                          limit = 1, startFromHead = True)
#Prints out the persons first language
print(nativeLang)
#Prints out the last 4 letters of the b64 audio
print(audio64[-4:])

file = open("testaudio.txt","w")
file.write(audio64)
file.close()