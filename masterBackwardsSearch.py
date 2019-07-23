import boto3
import json
client = boto3.client('logs')
"""Starts with a log event and goes back in time until it finds the correct information (L1, b64, etc.)
:param logStream: the log stream where the error is located
:param backToken: the token given by the error event that allows us to move back in time
:param error: the type of error we are dealing with
:param ending: "transcript" or "expectedPhonemes" depending on if it is an alignment error or not
:returns: log event with info from the same log stream as the error
"""
def goBackToInfo(logStream, backToken, error, ending):
    while(True):
        newEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                          logStreamName=logStream,
                                          nextToken=backToken,
                                          limit = 1, startFromHead = True)
        events = newEvent['events']
        if len(events) == 0:
            return None
        spliced = events[0]['message'].split("\"")
        if "L1" in spliced and error in spliced:
            if ending not in spliced:
                currentEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                            logStreamName=logStream,
                                            nextToken=newEvent['nextForwardToken'],
                                            limit = 1, startFromHead = True)
                newEvent['events'][0]['message'] += currentEvent['events'][0]['message']
                lastEvent = currentEvent
                while ending not in currentEvent['events'][0]['message']:
                    currentEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                                logStreamName=logStream,
                                                nextToken=lastEvent['nextForwardToken'],
                                                limit = 1, startFromHead = True)
                    lastEvent = currentEvent
                    newEvent['events'][0]['message'] += currentEvent['events'][0]['message']
                #This is to deal with the weird formatting of the log event
                splice = currentEvent['events'][0]['message'].split("[")
                splice = splice[-1]
                splice = splice[:-2]        
                splice = splice[:-1]
                splice = "[" + splice
                newEvent['events'][0]['message'] += splice

            #jsonEvents = json.dumps(newEvent, indent = 4, sort_keys = True)
            return newEvent['events'][0]['message']
        backToken = newEvent['nextBackwardToken']
        
