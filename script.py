import json
import requests
from lxml import html

class MediumScraper:
	'''
	IDEAS
	- extract handclap posts
	- extract user highlights from posts because it will
	be like going through snippets
	- login to extract user bookmarks
	'''
	
	def __init__(self, username):
		self.username = username


	def getUserProfile(self):
		'''
		Returns the user profile that is currently being feteched
		'''
		return('https://medium.com/@'+self.username+'/')

	def getRequest(self):
		'''
		Gets the `claps` of the user profile
		'''
		URL = 'https://medium.com/@'+self.username+'/has-recommended'
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


if __name__ == '__main__':
	# main()

	obj = MediumScraper('tharangni')
	a, b = obj.parseHTML(obj.getRequest())

	with open('user.json', 'w') as f:
		json.dump(a, f)

	with open('claps.json', 'w') as g:
		json.dump(b, g)