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
import cfscrape

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
	# open file, write in log
	with open('mentionLog.txt', 'w') as outfile:
		json.dump(mentionLog, outfile)

# 1. Submite an URL
# 2. Get archive.is new URL
def archive(convertUrl):
	url = "http://archive.is/submit/"
	print("Connecting to archive.is..")
	# s = requests.Session()
	# r = requests.post(url,data = {'url':convertUrl})
	
	# bypass cloudflare
	scraper = cfscrape.create_scraper()
	r = scraper.post(url,data = {'url':convertUrl})
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
			mentionLog.append(str(mention.created_at))
			writeLog(mentionLog)
			try:
				# Check if just an url
				convertUrl = mention.entities['urls'][0]['expanded_url']
			except:
				print("Not URL only")
				# with open('test.js', 'w') as outfile:
				# 	outfile.write(str(mention))
				try:
					# Check if reply to a tweet
					checkIfReply = mention.in_reply_to_status_id
					if(str(checkIfReply) == "None"):
						print("Error in getting id #")
						exit()
					convertUrl = "https://twitter.com/statuses/"
					convertUrl += str(checkIfReply)
				except:
					print("Not reply, not URL")
					exit()
			username = mention.user.screen_name
			tweetId = mention.id
		else:
			print("No new Tweets!")
			exit(2)

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
