import os
import re
import json
import string
import scrapy
import requests

import numpy as np
import pandas as pd

from lxml import html

from datetime import datetime
from collections import Counter

from nltk import tokenize
from nltk.corpus import stopwords



def saveJSON(path, data):

	# writes json data to file path

	json_data = json.loads(data)
	with open(path, 'w') as file:
		json.dump(json_data, file)


def parseJSON(json_file):
	
	# @todo: read json and extract only relevant fields

	read_file = pd.read_json(json_file, lines=True)
	return read_file


def sentenceCounter(sentence: str) -> int:

	# return number of sentences in paragraph

	split = tokenize.sent_tokenize(sentence)
	return len(split)


def preprocessQuote(text: str) -> str:

	# return preprocessed quote

	stop_words = set(stopwords.words('english'))
	
	words = re.split(r'\W+', text.lower())
	table = str.maketrans('', '', string.punctuation)
	stripped = [w.translate(table) for w in words]
	stopped = [w for w in stripped if not w in stop_words]
	sentence = ' '.join([str(w) for w in stopped])
	
	return sentence


class MediumScraper:
	'''
	IDEAS
	- extract handclap posts
	- extract user highlights from posts because it will
	be like going through snippets
	- login to extract user bookmarks
	- more can be done with the extracted highlights. For ex: using the extracted highlights you can: 
		- create a summary of your "highlights" in the form of a word cloud
		- classify the whole set into topics using unsupervised learning or etc
		-- this might give you an idea of the topics which you like to read!!![COOL]

	'''
	
	def __init__(self, username):
		self.username = username


	def getUserProfile(self):
		'''
		Returns the user profile that is currently being feteched
		'''
		return('https://medium.com/@'+self.username+'/')


	def getClapsURL(self, limit):
		'''
		Returns the url for claps
		'''
		return self.getUserProfile()+'has-recommended?format=json&limit={}'.format(limit)


	def getHighlightsURL(self, limit):
		'''
		Returns the url for highlights
		'''
		return '{}highlights?format=json&limit={}'.format(self.getUserProfile(), limit)


	def getRequest(self):
		'''
		Gets the `claps` of the user profile
		'''
		URL = self.getClapsURL(500)
		medium_recommend = requests.get(URL)
		tree = html.fromstring(medium_recommend.content)

		return tree


	def parseHTML(self, tree):
		'''
		Goes to /html/body/script[3] & [4] which has all content
		returns: userjson and clapsjson
		'''
		self.tree = tree
		if self.tree is not None:
			userJsonScript = self.tree.xpath('//body/script[3]/text()')[0].split('=')[1]
			clapsJsonScript = self.tree.xpath('//body/script[4]/text()')[0].split('=')[1]
			
			userJson = json.loads(userJsonScript)
			clapsJson = json.loads(clapsJsonScript)

		return userJson, clapsJson


class ClapsScraper(scrapy.Spider):
	'''
	docstring for ClapsScraper
	'''
	name = "claps_scraper"
	handle_http_list = [400, 401]
	auto_throttle_enable = True
	

	def start_requests(self):

		user = MediumScraper('tharangni')
		
		start_urls = [user.getClapsURL(1000)]

		for url in start_urls:
			yield scrapy.Request(url, method='GET', callback=self.parse)

	def parse(self, response):

		response_data = response.text
		response_split = response_data.split("while(1);</x>")
		response_data = response_split[-1].strip()

		dt_string = datetime.now().strftime("%d%m%Y_%H%M%S")
		filename = "medium_{}_claps_{}.json".format('tharangni', dt_string)

		saveJSON(filename, response_data)		

		pass		


class HighlightsScraper(scrapy.Spider):
	'''
	docstring for HighlightsScraper
	'''
	name = "highlights_scraper"
	handle_http_list = [400, 401]
	auto_throttle_enable = True
	

	def start_requests(self):

		user = MediumScraper('tharangni')
		
		start_urls = [user.getHighlightsURL(500)]

		for url in start_urls:
			yield scrapy.Request(url, method='GET', callback=self.parse)

	def parse(self, response):

		response_data = response.text
		response_split = response_data.split("while(1);</x>")
		response_data = response_split[-1].strip()

		dt_string = datetime.now().strftime("%d%m%Y_%H%M%S")
		filename = "medium_{}_highlights_{}.json".format('tharangni', dt_string)

		saveJSON(filename, response_data)		

		pass		


class ClapsTable(object):
	"""
	docstring for ClapsTable
	"""
	def __init__(self, json_file):
		super(ClapsTable, self).__init__()
		self.df = pd.read_json(json_file)


	def getDataFrame(self):

		post_ids = self.df['payload']['references']['Post'].keys()
		posts_df = pd.DataFrame(index = post_ids, columns=['postId', 'title', 'subtitle', 'homeCollectionId', 
												   'postedAt', 'uniqueSlug', 'creatorId', 'tags', 'totalClapCount',
												  'userClapCount', 'readingTime'])

		posts_df['postId'] = post_ids
		for key in post_ids:
			posts_df.at[key, 'title'] = self.df['payload']['references']['Post'][key]['title']
			posts_df.at[key, 'postedAt'] = int(str(self.df['payload']['references']['Post'][key]['firstPublishedAt'])[:-3])
			posts_df.at[key, 'uniqueSlug'] = self.df['payload']['references']['Post'][key]['slug']+'-'+key
			posts_df.at[key, 'homeCollectionId'] = self.df['payload']['references']['Post'][key]['homeCollectionId']
			posts_df.at[key, 'creatorId'] = self.df['payload']['references']['Post'][key]['creatorId']
			posts_df.at[key, 'totalClapCount'] = self.df['payload']['references']['Post'][key]['virtuals']['totalClapCount']
			posts_df.at[key, 'userClapCount'] = self.df['payload']['references']['Post'][key]['virtuals']['sectionCount']
			posts_df.at[key, 'readingTime'] = round(self.df['payload']['references']['Post'][key]['virtuals']['readingTime'])
			posts_df.at[key, 'tags'] = [tag['slug'] for tag in self.df['payload']['references']['Post'][key]['virtuals']['tags']]
			
			try:
				posts_df.at[key, 'subtitle'] = self.df['payload']['references']['Post'][key]['content']['subtitle']
			except:
				posts_df.at[key, 'subtitle'] = np.nan
			

		return posts_df


class HighlightsTable(object):
	"""
	docstring for HighlightsTable
	"""
	def __init__(self, json_file):
		super(HighlightsTable, self).__init__()
		self.df = pd.read_json(json_file)


	def getDataFrame(self):

		quote_ids = self.df['payload']['references']['Quote'].keys()
		post_ids = self.df['payload']['references']['Post']

		quote_df = pd.DataFrame(index = quote_ids, columns=['quoteId', 'postId', 'highlightedAt', 'highlightDate',
												   'highlightTimeHour', 'highlightTimeDoW', 'postTitle',
												   'quoteText', 'numOfSentences', 'numOfWords', 'language', 'tags'])

		quote_df['quoteId'] = quote_ids
		
		for key in quote_ids:
			

			quote_df.at[key, 'postId'] = self.df['payload']['references']['Quote'][key]['postId']
			quote_df.at[key, 'highlightedAt'] = int(str(self.df['payload']['references']['Quote'][key]['createdAt'])[:-3])
			quote_df.at[key, 'highlightDate'] = datetime.utcfromtimestamp(quote_df.at[key, 'highlightedAt']).strftime('%d-%m-%Y %H:%M:%S')
			quote_df.at[key, 'highlightTimeDoW'] = datetime.utcfromtimestamp(quote_df.at[key, 'highlightedAt']).strftime('%A')
			quote_df.at[key, 'highlightTimeHour'] = datetime.utcfromtimestamp(quote_df.at[key, 'highlightedAt']).strftime('%H')    
			
			begin = self.df['payload']['references']['Quote'][key]['startOffset']
			end = self.df['payload']['references']['Quote'][key]['endOffset']
			quote_df.at[key, 'quoteText'] = self.df['payload']['references']['Quote'][key]['paragraphs'][0]['text'][begin:end]
			
			quote_df.at[key, 'numOfSentences'] = sentenceCounter(quote_df.at[key, 'quoteText'])
			quote_df.at[key, 'numOfWords'] = len(quote_df.at[key, 'quoteText'].split(" "))
			quote_df.at[key, 'postTitle'] = post_ids[quote_df.at[key, 'postId']]['title']
			quote_df.at[key, 'language'] = post_ids[quote_df.at[key, 'postId']]['detectedLanguage']    
			quote_df.at[key, 'tags'] = [tag['slug'] for tag in post_ids[quote_df.at[key, 'postId']]['virtuals']['tags']]

		return quote_df
		

	def getWordFrequencies(self, df, column):

		word_freq = Counter()
		
		a = df[column].drop_duplicates(keep=False, inplace=False)
		a = a.apply(lambda x: preprocessQuote(x))
		b = list(a)

		for sent in b:
			for word in sent.split(' '):
				if word.isalpha() and len(word)>1:
					word_freq[word]+=1

		wf_df = pd.DataFrame.from_dict(word_freq, orient='index').reset_index()
		wf_df.columns = ['word', 'freq']

		return wf_df



if __name__ == '__main__':

	# os.system("scrapy runspider script.py")

	# claps = ClapsTable("medium_tharangni_claps_23102019_200135.json")
	# clapsDf = claps.getDataFrame()
	# clapsDf.to_csv("claps_v1.csv", index=False)

	highlights = HighlightsTable("medium_tharangni_highlights_08112019_232305.json")
	
	quoteDf = highlights.getDataFrame()
	quoteDf.to_csv("highlights_v1.csv", index=False)
	
	wordFreqDf = highlights.getWordFrequencies(quoteDf, 'quoteText')
	wordFreqDf.to_csv("word_freq_highlights_v1.csv", index=False)

	titleFreqDf = highlights.getWordFrequencies(quoteDf, 'postTitle')
	titleFreqDf.to_csv("word_freq_title_v1.csv", index=False)
	
