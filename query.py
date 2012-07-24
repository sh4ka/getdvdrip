import urllib2
import json
import logging

import configuration
import api

def query_api():
	result = {}
	query_url = configuration.DVDRELEASESURL+api.API+configuration.DVDPAGELIMIT
	try:
		u = urllib2.urlopen(query_url)
		result = u.read()
	except Exception, e:
		logging.error('RELEASES API ERROR')
	return result.strip()

def query_movie(title):
	result = {}
	query_url = configuration.MOVIEURL+api.API+configuration.QUERYPARAM+title
	try:
		u = urllib2.urlopen(query_url)
		result = u.read()
	except Exception, e:
		logging.error('MOVIES API ERROR')
	return result.strip()

def query_torrent(search):
	result = {}
	if search:		
		query_url = configuration.QUERYURL+search+configuration.ORDERSTRING+configuration.LIMITSTRING+configuration.FORMATSTRING+configuration.CATEGORYMOVIESSTRING
		try:
			u = urllib2.urlopen(query_url)
			result = json.loads(u.read())
		except Exception, e:
			logging.error('SEARCH ERROR')
	return result
