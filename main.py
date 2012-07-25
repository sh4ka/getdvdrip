import os
import webapp2
import jinja2
import urllib2
import logging
import json
import datetime
import time
import cgi
import hashlib

from google.appengine.api import memcache
from google.appengine.ext import db

# modules
import configuration
import query
import cookies

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
	autoescape = True)

class Handler(webapp2.RequestHandler):
	"""URL handler"""
	def write(self, *a, **kw):
		self.response.out.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render(self, template, **kw):
		self.write(self.render_str(template, **kw))

class MainPage(Handler):
	"""Main page function"""
	def get(self):
		uid = cookies.get_cookie(self, 'uid')
		if uid is None:
			cookies.set_cookie(self, 'uid', hashlib.sha1(str(time.time())).hexdigest(), 'never' )
		today = datetime.date.today()
		releases = get_today_release(str(today))
		self.render('front.html', releases = releases)

	def post(self):
		search = self.request.get('search')
		search = urllib2.quote(cgi.escape(search))
		self.redirect('/search/'+search)

class SearchResults(Handler):
	"""Main page function"""
	def get(self, search):
		search = urllib2.quote(cgi.escape(search))
		self.render('results.html', releases = get_title(search))
	def post(self, search):
		search = self.request.get('search')
		search = urllib2.quote(cgi.escape(search))
		self.redirect('/search/'+search)

class SearchMagnet(Handler):
	"""Search function"""
 	def get(self):
 		search = self.request.get('search')
 		search = urllib2.quote(cgi.escape(search))
 		output = query.query_torrent(search)
		output = add_trackers_to_magnets(output)
		self.response.headers['Content-Type'] = "application/json"		
		self.write(json.dumps(output))

class Release(db.Model):
    data = db.TextProperty(required = True)
    created = db.DateProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Movie(db.Model):
	title = db.StringProperty(required = True)
	data = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

def get_today_release(today):
	key = today
	releases = memcache.get(key)
	if releases is None:
		logging.info('DB QUERY')
		q = db.Query(Release)
		q.filter('created =', datetime.date.today()).order('-created')
		result = q.fetch(limit=1)
		if len(result) > 0:
			logging.info('RELEASE FOUND IN DB')
			row = result[0]	
			releases = row.data
			memcache.set(key, releases)
		if releases is None:
			logging.info('FETCHING RELEASE API')
			releases = query.query_api()
			r = Release(data = releases)
			r.put()
			memcache.set(key, releases)
	return json.loads(releases)

def get_title(title):
	title_url = urllib2.unquote(title)
	title_url = title_url.replace(' ', '-')
	title_url = title_url.lower()
	title = urllib2.quote(title_url.replace('-', ' '))
	key = title_url
	movie = memcache.get(key)
	if movie is None:
		logging.info('DB QUERY')
		q = db.Query(Movie)
		q.filter('title =', key)
		result = q.fetch(limit=1)
		if len(result) > 0:
			logging.info('MOVIE FOUND IN DB')
			row = result[0]
			movie = row.data
			memcache.set(key, movie)
		if movie is None:
			logging.info('FETCHING MOVIE FROM API')
			movie = query.query_movie(title)
			m_dict = json.loads(movie)
			if m_dict['total'] != 0:
				m = Movie(title = key, data = movie)
				m.put()
				memcache.set(key, movie)
			else:
				movie = '{}'
	return json.loads(movie)

def add_trackers_to_magnets(magnet_list):
	for item in magnet_list:		
		item['magnet'] += configuration.TRACKERS
	return magnet_list


app = webapp2.WSGIApplication([
					('/', MainPage),
					('/search/(.+)', SearchResults),
					('/search_magnet.json', SearchMagnet)
					], debug=True)
 				 		