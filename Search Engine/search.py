from textProcessing import cleanup_string
from collections import defaultdict
import threading, sys, bz2, re, math, pdb
from config import *
import time

offset = []

def ranking(results, documentFreq, numberOfFiles):

    listOfDocuments, idf_of_word = defaultdict(float), defaultdict(float)


    for word in documentFreq:
        idf_of_word[word] = math.log((float(numberOfFiles)/(float(documentFreq[word]) + 1)))

    for word in results:
        fieldWisePostingList = results[word]
        for field in fieldWisePostingList:
            if len(field) > 0:


                postingList = fieldWisePostingList[field]


                postingList = postingList[:TOP_N_POSTINGS_FOR_EACH_WORD*2] if CONSIDER_TOP_N_POSTINGS_OF_EACH_WORD else postingList


                factor = FIELD_WEIGHTS[field]

                for i in range(0, len(postingList), 2):
                    listOfDocuments[postingList[i]] += math.log(1+float(postingList[i+1])) * idf_of_word[word] * factor

    return listOfDocuments



def findFileNumber(low, high, offset, pathOfFolder, word, f):

    while low <= high:
        mid = (low+high)/2
        f.seek(offset[mid])
        testWord = f.readline().strip().split(' ')


        if word == testWord[0]:

            return testWord[1:], mid
        elif word > testWord[0]:
            low = mid+1
        else:
            high = mid-1
    return [], -1


def findFileNumber_forTitleSearch(low,high,offset,pathOfFolder,word,f):

    word = int(word)
    while low <= high:
        mid = (low+high)/2
        f.seek(offset[mid])
        testWord = f.readline().strip().split(' ')

        if word == int(testWord[0]):
            return testWord[1:], mid
        elif word > int(testWord[0]):
            low = mid+1
        else:
            high = mid-1
    return [], -1


def findFileList(fileName, fileNumber, field, pathOfFolder, word, fieldFile):

    fieldOffset, tempdf = [], []

    offsetFileName = pathOfFolder + '/o' + field + fileNumber + '.txt'
    with open(offsetFileName,'rb') as fieldOffsetFile:
        for line in fieldOffsetFile:
            offset, docfreq = line.strip().split(' ')
            fieldOffset.append(int(offset))
            tempdf.append(int(docfreq))
    fileList, mid = findFileNumber(0, len(fieldOffset), fieldOffset, pathOfFolder, word, fieldFile)
    return fileList, tempdf[mid]


def queryMultifield(queryWords, listOfFields, pathOfFolder, fVocabulary):

    fileList = defaultdict(dict)
    df = {}
    for i in range(len(queryWords)):
        word, key = queryWords[i], listOfFields[i]
        returnedList, mid= findFileNumber(0, len(offset), offset, sys.argv[1], word, fVocabulary)
        if len(returnedList) > 0:
            fileNumber = returnedList[0]
            fileName = pathOfFolder+'/'+key+str(fileNumber)+('.bz2' if COMPRESS_INDEX else ".txt")
            fieldFile = bz2.BZ2File(fileName,'rb') if COMPRESS_INDEX else open(fileName)
            returnedList, docfreq = findFileList(fileName,fileNumber,key,pathOfFolder,word,fieldFile)
            fileList[word][key], df[word] = returnedList, docfreq
    return fileList, df


def main():
    if len(sys.argv)!= 2:
        print "Usage :: python wikiIndexer.py pathOfFolder"
        sys.exit(0)

    # Read the offsets
    with open(sys.argv[1] + '/offset.txt', 'rb') as f:
        for line in f:
            offset.append(int(line.strip()))

    # Read the title offsets
    titleOffset = []
    with open(sys.argv[1]+'/titleoffset.txt','rb') as f:
        for line in f:
            titleOffset.append(int(line.strip()))
	fVocabulary = open(sys.argv[1] + '/vocabularyList.txt', 'r')
	voc = {}
	for i in fVocabulary.readlines():
		voc[i.strip().split()[0]] = 1
	print(len(voc))

    while True:
        query = raw_input("Enter query:")
	if len(query.strip()) < 1:
	    sys.exit(0)
	start_time = time.time()

        queryWords = query.strip().split(' ')
        listOfFields, temp = [], []
        for word in queryWords:
            if re.search(r'[t|b|c|e|i]{1,}:', word):
                _fields = list(word.split(':')[0])
		_words = [word.split(':')[1]] * len(_fields)
            else:
		_fields = ['t', 'b', 'c', 'e', 'i']
			# print(voc.get('gogle',-1))
			# print(k)
		_words = [word] * len(_fields)

            listOfFields.extend(_fields)
            temp.extend(cleanup_string(" ".join(_words)))

	print("Fields:", listOfFields)
	print("Words:", temp)
        print("="*40)
        results, documentFrequency = queryMultifield(temp, listOfFields, sys.argv[1], fVocabulary)

        with open(sys.argv[1]+'/numberOfFiles.txt','r') as f:
            numberOfFiles = int(f.read().strip())

        results = ranking(results, documentFrequency, numberOfFiles)
	end_time = time.time()
        if len(results)>0:
            top_n_docs = sorted(results, key=results.get, reverse=True)[:TOP_N_RESULTS]


            titleFile = open(sys.argv[1] + '/title.txt','rb')
            dict_Title = {}
            for docid in top_n_docs:                                                                  #find top ten links
                title, _ = findFileNumber_forTitleSearch(0, len(titleOffset), titleOffset, sys.argv[1], docid, titleFile)
                if not len(title):
                    print("Title Not Found:", docid, titleFile, len(titleOffset))
                dict_Title[docid] = ' '.join(title)

            for rank, docid in enumerate(top_n_docs):
                print"\t",rank+1, ":", dict_Title[docid], "(Score:", results[docid], ")"
            print("="*40)
	    print("QueryTime:", end_time - start_time, "seconds")
        else:
            print ("Phrase Not Found")


if __name__ == "__main__":
    main()
