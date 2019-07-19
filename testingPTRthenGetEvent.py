import boto3
import json
from BackwardsSearch import goBackToInfo
logs = 15
client = boto3.client('logs')
streams = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                logStreamName="2019/07/16/[176]26f6b7d8b68945489410513a94c3fce7",
                                startTime=1563316751068,
                                endTime=1563316751070,
                                limit = 1, startFromHead = True)
print(json.dumps(streams, indent = 3, sort_keys = True))

file = open("testformat.json","w")
file.write(json.dumps(streams, indent = 3, sort_keys = True))
file.close()