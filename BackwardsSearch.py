import boto3
import json
client = boto3.client('logs')
#This takes two parameters. The logStream the event is located in and the backToken
#It starts rom that token and then keeps going back until it finds the info event
def goBackToInfo(logStream, backToken):
    while(True):
        newEvent = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                          logStreamName=logStream,
                                          nextToken=backToken,
                                          limit = 1, startFromHead = True)
        events = newEvent['events']
        spliced = events[0]['message'].split("\"")
        dataIndex = None
        for x in range(0, len(spliced)) :
            #The L1 string is unique only to the type of event we want
            if spliced[x] == "L1":
                #In the spliced array, the b64 audio file is 6 past the"L1" string
                #If the last character in the array is not a =, then there is more in the next event
                if spliced[x+6][-1] != '=':
                    event2 = client.get_log_events(logGroupName='/aws/lambda/ml-coordinator', 
                                                        logStreamName=logStream,
                                                        nextToken=newEvent['nextForwardToken'],
                                                        limit = 1, startFromHead = True)
                    #This is to deal with the weird formatting of the log event
                    splice = event2['events'][0]['message'].split("[")
                    splice = splice[-1]
                    splice = splice[:-2]        
                    splice = splice[:-1]
                    splice = "[" + splice

                    newEvent['events'][0]['message'] += event2['events'][0]['message']
                    #print(streams['events'][0]['message'])
                    newEvent['events'][0]['message'] += splice
                jsonEvents = json.dumps(newEvent, indent = 4, sort_keys = True)
                return jsonEvents
        backToken = newEvent['nextBackwardToken']
    
