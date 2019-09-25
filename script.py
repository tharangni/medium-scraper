import re
import json
import scrapy
import requests

import pandas as pd

from lxml import html
from datetime import datetime



def saveJSON(path, data):

	# writes json data to file path

	with open(path, 'w') as file:
		json.dump(data, file)


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


	def getClapsURL(self):
		'''
		Returns the url for claps

		'''
		return self.getUserProfile()+'has-recommended'
		# return 'https://www.medium.com/search/posts?q=Data%20Science'


	def getRequest(self):
		'''
		Gets the `claps` of the user profile
		'''
		URL = self.getClapsURL()
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
		
		start_urls = [user.getClapsURL()]

		# cookie = "__cfduid=d13dc96d7996d6bf5168dc50cf43610881546335152; uid=1e473cbcde46; sid=1:D2btGU5i9eacrLuBlsVoMMEQvrl8QBPMuE5hxBDfHyQDXw0bxZfnthWzo9/4jBqq; lightstep_guid/lite-web=4bb788422492a14e; lightstep_session_id=33a3ad460d691fcb; pr=1; tz=-120; sz=1351; xsrf=3std0BPdCjMD; __cfruid=59e31e646a3b110fdde50a4b3e2efffd626fbe49-1569357959"
		# header = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"

		for url in start_urls:
			yield scrapy.Request(url, method='GET', callback=self.parse)

	def parse(self, response):

		response_data = response.text
		response_split = re.findall(r'<script>(.*?)</script>', response_data)
		response_data = response_split[3:]

		dt_string = datetime.now().strftime("%d%m%Y_%H%M%S")
		filename = "medium_{}_claps_{}.json".format('tharangni', dt_string)

		saveJSON(filename, response_data[-2].split("window.__APOLLO_STATE__ =")[-1])

		df = parseJSON(filename)
		
		print(df.head(5))

		pass		


if __name__ == '__main__':

	# r = parseJSON("user.json")
	# print(r)

	# main()

	obj = MediumScraper('tharangni')
	print(obj.getClapsURL())
	# a, b = obj.parseHTML(obj.getRequest())

	# with open('user.json', 'w') as f:
	# 	json.dump(a, f)

	# with open('claps.json', 'w') as g:
	# 	json.dump(b, g)