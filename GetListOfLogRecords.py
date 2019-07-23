"""This takes all of the results from the query, collects the unique ptrs, and returns that list
:param results: all the log events in that time frame that satisfied the query
:returns: the list of unique ptrs
"""

def getListOfUniquePTR(results):
    logsWithErrors = []
    ptrRecords = []

    for i in range(0, len(results['results'])):
        """
        Every set of log events has a start and end log. Every log in that set has a similar identifier
        that we can find always at the 25:60 substring in 'value'. The log events that have the same identifier
        will point to the same audio file and transcript so we collect this to avoid duplicates
        """
        identifier = results['results'][i][1]['value'][25:60]
        #This gets the ptr value which tells us the record and timestamp of the log entry
        ptr = results['results'][i][2]['value']
        #Checks to make sure there is no log from the same set (they would point to the same information)
        if identifier not in logsWithErrors:
            logsWithErrors.append(identifier)
            ptrRecords.append(ptr)
    return ptrRecords