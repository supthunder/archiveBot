#!/usr/bin/env python3
from bs4 import BeautifulSoup
import requests
import re
import json
import urllib.request
from time import gmtime, strftime
import tweepy
from tokens import *
import os
import time

# setup twitter
auth = tweepy.OAuthHandler(C_KEY, C_SECRET)  
auth.set_access_token(A_TOKEN, A_TOKEN_SECRET)  
api = tweepy.API(auth)
username = ""
tweetId = ""


# Tweet link
def tweet(archiveUrl):
    tweet = "@"+username+"\n"
    tweet += "Archived link:\n"
    tweet += archiveUrl+"\n"
    tweet += strftime("%Y-%m-%d %H:%M:%S", gmtime())
    print(tweet)
    api.update_status(tweet,tweetId)

# Load mention log
# This keeps track of mentions
def loadLog():
    # # open file, read in log
    with open('mentionLog.txt', 'r') as outfile:
    	mentionLog = json.load(outfile)
    return mentionLog

# Write mention log
# This keeps track of mentions
def writeLog(mentionLog):
	# Remove previous user
	while(len(mentionLog) > 100):
		mentionLog.pop()
	# open file, write in log
	with open('mentionLog.txt', 'w') as outfile:
		json.dump(mentionLog, outfile)

# 1. Submite an URL
# 2. Get archive.is new URL
def archive(convertUrl):
	url = "http://archive.is/submit/"
	s = requests.Session()
	# r2 = s.get('http://archive.is/')
	# time.sleep(3)
	r = s.post(url,data = {'url':convertUrl})

	soup = BeautifulSoup(r.text,"html.parser")
	linkRegex = re.compile("(?<=\(\").*(?=\"\))")
	archiveUrl = soup.find('script')
	archiveUrl = re.search(linkRegex, str(archiveUrl)).group(0)

	if(archiveUrl == "DIVSHARE"):
		print("Link already archived!")
		archiveUrl = (soup.findAll(attrs={"itemprop":"url"}))
		archiveUrl = str(archiveUrl[0]['content'].encode('utf-8')).replace('b','').replace('\'','')

	return archiveUrl

# 1. Get latest twitter mentions
# 2. Tweet with archived URL
def getMentions():
	mentionLog = loadLog()
	convertUrl = ""
	mentions = api.mentions_timeline(count=1)
	global username
	global tweetId
	for mention in mentions:
		if str(mention.created_at) not in mentionLog:
			try:
				convertUrl = mention.entities['urls'][0]['expanded_url']
			except:
				print("No URL")
				exit(1)
			username = mention.user.screen_name
			tweetId = mention.id
			mentionLog.append(str(mention.created_at))
			writeLog(mentionLog)
		else:
			print("No new Tweets!")
			exit(1)

	archiveUrl = archive(convertUrl)
	tweet(archiveUrl)

# Quits if error
def main():
	try:
		 getMentions()
	except:
		print("Error")
		exit(1)
main()