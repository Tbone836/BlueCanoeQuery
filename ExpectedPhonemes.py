def expectedPhonemesOrganize(notFormattedData, events):
    notFormattedData = notFormattedData.split('\"')

    listExpectedPhonemes = notFormattedData[-1*(len(notFormattedData)-notFormattedData.index('expectedPhonemes')-1):]
  
    dictJson = {}
    dictJson['requestID'] = events['ResponseMetadata']['RequestId']
    dictJson['L1'] = notFormattedData[notFormattedData.index('L1')+2]
    dictJson['b64Audio'] = notFormattedData[notFormattedData.index('b64Audio')+2]
    phonemeArray = []
    phonemeDict={}
    for x in range(0, len(listExpectedPhonemes)):
        currentWord = listExpectedPhonemes[x]
        #The spliced array is like ['[{', 'word', ':', 'red', '},{' , 'isFocusWord , :false}]]
        #It repeats itself every six indexes so the 3 is the distance the value of 'word' from a mod 6
        if currentWord == 'startTime':
            start = listExpectedPhonemes[x+1]
            start = start.split("}")
            phonemeDict['startTime'] = start[0][1:]
        elif currentWord == 'endTime':
            phonemeDict['endTime'] = listExpectedPhonemes[x+1][1:-1]
        elif currentWord == 'phoneme':
            phonemeDict['phoneme'] = listExpectedPhonemes[x+2]
        if 'startTime' in phonemeDict.keys() and 'endTime' in phonemeDict.keys():
            if 'phoneme' in phonemeDict.keys():
                phonemeArray.append(phonemeDict)
                phonemeDict = {}
    dictJson['expectedPhonemes'] = phonemeArray
    return dictJson