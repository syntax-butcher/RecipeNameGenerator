#!/usr/bin/env python

print 'Content-Type: text/plain'
print

import sys
import httplib
import cgi
from xml.dom.minidom import parseString
import array
import random
import urllib


prepprob = 1
adjprob = .25
dishprob = .25
freqmin = 100000

debugmode = 0


def AddDescriptor(rootword, filename, prob, after):
	rootword.strip()
	randdraw = random.random()
	if (randdraw <= prob):
		wordlist = GetListFromFile(filename)
		element = random.randint(0,len(wordlist)-1)
		if (after==0):
			rootword = wordlist[element] + " " + rootword
		else:
			rootword = rootword + " " + wordlist[element]
	return rootword.strip()
	
def GetListFromFile(filename):
	listfile = open(filename, "r")
	listitem = "startseed"
	wordlist = []
	listitem = listfile.readline(1000)	# 1000 chars max
	while (listitem != ""):
		wordlist.append(listitem.strip())
		listitem = listfile.readline(1000)	# 1000 chars max		
	return wordlist
			
def GetWordFrequency(keyword):
	targetyear = "2006"
	freqscore = 0
	maxword = "the"
	occurrences = 0
	useratiofreq = 0	# use ratio for frequency score (else use raw count)
	
	if (useratiofreq == 1):
		# most common word is "the", so calculate frequency score based on that
		url = "/api/word.xml/" + maxword + "/frequency"
		conn.request("GET", url, "", headers)
		output = conn.getresponse()
		
		frequencysumm = output.read()
		domxml = parseString(frequencysumm)
		freqelements = domxml.getElementsByTagName("frequency")
		
		for item in freqelements:
			year = item.childNodes[1].childNodes[0].childNodes[0].nodeValue
			if (year == targetyear):
				max = item.childNodes[0].childNodes[0].childNodes[0].nodeValue
			
	# now get target word frequency and calculate its score
	url = "/api/word.xml/" + keyword + "/frequency"
	conn.request("GET", url, "", headers)
	output = conn.getresponse()
	
	frequencysumm = output.read()
	domxml = parseString(frequencysumm)
	freqelements = domxml.getElementsByTagName("frequency")
	
	for item in freqelements:
		year = item.childNodes[1].childNodes[0].childNodes[0].nodeValue
		if (year == targetyear):
			occurrences = item.childNodes[0].childNodes[0].childNodes[0].nodeValue
	
	if (useratiofreq == 1):
		# calculate ratio of given word count to max word count
		freqscore = float(occurrences) / float(max)
	else:
		# just use raw word count
		freqscore = occurrences
		
	return freqscore		

if __name__ == '__main__':
	params = {}
	if (debugmode == 0):
		fieldStorage = cgi.FieldStorage()
		for key in fieldStorage.keys():
			params[key] = fieldStorage[key].value
		
	else:
		params = {"food1":"chicken","food2":"rice"}
	
	inputwords = len(params)
	
	conn = httplib.HTTPConnection("api.wordnik.com")
	#headers = {"api_key":"e3a0d886f10c3972df2cd40529d0cb96faaa8304b44270228"}
	headers = {"api_key":"726bdc18913a01ef41002052f4a04e781ebd3f4f737557e47"}
	haspos = 0
	hasdef = 0
	word = []

	urlparams = ""
	urlparams += "minDictionaryCount=1"		# must have a definition
	urlparams += "&"
	urlparams += "minCorpusCount=" + str(freqmin)
	urlparams += "&"
	urlparams += "includePartOfSpeech=adjective"

	# get random word for every input word given by user
	for wordcount in range(0,inputwords):
		url = "/api/words.xml/randomWord?" + urlparams
		conn.request("GET", url, "", headers)
		output = conn.getresponse()
		domxml = parseString(output.read())
#if (debugmode==1):
		#	print(domxml.getElementsByTagName("word")[0].childNodes[1].childNodes[0].nodeValue)

		newword = domxml.getElementsByTagName("wordObject")[0].childNodes[1].childNodes[0].nodeValue + ""
		newword = newword.encode('utf-8')
		word.append(newword)
		
	foodstring = ""
	random.seed()
	for i in range(0,inputwords):
		foodstring = AddDescriptor(foodstring, "adjectives.txt", adjprob, 0)
		foodstring += " " + word[i].strip()
		foodstring += " " + params[params.keys()[i]]
		if (inputwords>0 and i<inputwords-1):
			foodstring = AddDescriptor(foodstring, "prepositions.txt", prepprob, 1)
		
	foodstring = AddDescriptor(foodstring, "dishes.txt", dishprob, 1)
		
	print foodstring
