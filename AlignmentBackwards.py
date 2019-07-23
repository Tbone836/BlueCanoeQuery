import boto3
import json
client = boto3.client('logs')
#This takes two parameters. The logStream the event is located in and the backToken
#It starts rom that token and then keeps going back until it finds the info event
def goBackToInfoAlignment(logStream, backToken):
    while(True):
        newEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                          logStreamName=logStream,
                                          nextToken=backToken,
                                          limit = 1, startFromHead = True)
        events = newEvent['events']
        

        spliced = events[0]['message'].split("\"")
        if "L1" in spliced:
            if "transcript" not in spliced:
                currentEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                            logStreamName=logStream,
                                            nextToken=newEvent['nextForwardToken'],
                                            limit = 1, startFromHead = True)
                #This adds the other part of the audio file to newEvent's incomplete audio file
                newEvent['events'][0]['message'] += currentEvent['events'][0]['message']
                lastEvent = currentEvent
                while "transcript" not in currentEvent['events'][0]['message']:
                    currentEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                                logStreamName=logStream,
                                                nextToken=lastEvent['nextForwardToken'],
                                                limit = 1, startFromHead = True)
                    lastEvent = currentEvent
                    newEvent['events'][0]['message'] += currentEvent['events'][0]['message']
                #This is to deal with the weird formatting of the log event
                #This adds the transcript and its words to the newEvent's json file
                splice = currentEvent['events'][0]['message'].split("[")
                splice = splice[-1]
                splice = splice[:-2]        
                splice = splice[:-1]
                splice = "[" + splice
                newEvent['events'][0]['message'] += splice

            return newEvent['events'][0]['message']
        backToken = newEvent['nextBackwardToken']
        
