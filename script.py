import re
import json
import scrapy
import requests

import pandas as pd

from lxml import html
from datetime import datetime



def saveJSON(path, data):

	# writes json data to file path

	json_data = json.loads(data)
	with open(path, 'w') as file:
		json.dump(json_data, file)


def parseJSON(json_file):
	
	# @todo: read json and extract only relevant fields

	read_file = pd.read_json(json_file, lines=True)
	return read_file


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
		
		start_urls = [user.getClapsURL(500)]

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


# if __name__ == '__main__':

	# r = parseJSON("user.json")
	# print(r)

	# main()

	# scrapy = ClapsScraper()
	# scrapy.start_requests()

	# obj = MediumScraper('tharangni')
	# print(obj.getClapsURL())
	# a, b = obj.parseHTML(obj.getRequest())

	# with open('user.json', 'w') as f:
	# 	json.dump(a, f)

	# with open('claps.json', 'w') as g:
	# 	json.dump(b, g)