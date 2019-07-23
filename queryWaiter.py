import boto3
import time

"""This uses the time.sleep() function to wait and check if the query has finished. Then it returns the results
:param client: the connection to the aws logs
:response: the info about the query given to us after having started it.
:returns: the results of the finished query
"""
def queryWaitResults(client, response):
    status = client.get_query_results(queryId = response['queryId'])['status']
    count = 0
    #Keeps the query running until it is complete. Checks each second
    while(status != 'Complete'):
        time.sleep(1)
        status = client.get_query_results(queryId = response['queryId'])['status']
        print(str(count) + ": " + status)
        count += 1

    #This contains information on each log that satisfies the queryString
    #such as the timestamp and message it contains
    results = client.get_query_results(queryId = response['queryId'])
    return results