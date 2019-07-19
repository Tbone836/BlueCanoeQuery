import boto3
import json
from BackwardsSearch import goBackToInfo
logs = 15
client = boto3.client('logs')
streams = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                    logStreamName='2019/07/17/[176]f9d2603ee7e3423abd7a14e4504bf313',
                                    limit = 1, startFromHead = True)

for x in range(0,4):
    forwardToken = streams['nextForwardToken']
    streams = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                    logStreamName='2019/07/17/[176]f9d2603ee7e3423abd7a14e4504bf313',
                                    nextToken=forwardToken,
                                    limit = 1, startFromHead = True)

forwardToken = streams['nextForwardToken']
streams2 = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName='2019/07/17/[176]f9d2603ee7e3423abd7a14e4504bf313',
                                nextToken=forwardToken,
                                limit = 1, startFromHead = True)
print((streams['events'][0]['message']))
print(streams['events'][0].keys())
print(len(streams['events']))
def combineEvents(streams, streams2):
    splice = streams2['events'][0]['message'].split("[")
    splice = splice[-1]
    splice = splice[:-2]
    splice = splice[:-1]
    splice = "[" + splice

    streams['events'][0]['message'] += streams2['events'][0]['message']
    #print(streams['events'][0]['message'])
    streams['events'][0]['message'] += splice
    return streams

with open("testformat.json","w") as outfile:
    json.dump(streams, outfile, indent = 4, sort_keys = True)
