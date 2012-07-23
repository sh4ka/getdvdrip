import os
import webapp2
import jinja2
import urllib2
import logging
import json
import datetime
import cgi

from google.appengine.api import memcache
from google.appengine.ext import db

# modules
import configuration
import query

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
		today = datetime.date.today()
		today = '2012-07-23'
		releases = get_today_release(str(today))
		self.render('front.html', releases = releases)

	def post(self):
		search_term = self.request.get('search')	
		search_term = search_term.replace(' ', '-')
		self.redirect('/movie/'+search_term)

class SearchMagnet(Handler):
	"""Search function"""
 	def get(self):
 		search = self.request.get('search')
 		search = urllib2.quote(cgi.escape(search))
		self.response.headers['Content-Type'] = "application/json"
		output = query.query_torrent(search)
		self.write(json.dumps(output))

class MoviePermalink(Handler):
	"""Permalink"""
 	def get(self, title):
 		movie = get_title(title)
 		if movie:
 			self.render('movie.html', movie = movie)
 		else:
 			self.error(404)

 	def post(self, params):
 		title = self.request.get('search')
 		title = cgi.escape(title)
 		title = title.replace(' ', '-')
 		self.redirect('/movie/'+title)

class Release(db.Model):
    data = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

class Movie(db.Model):
	title = db.TextProperty(required = True)
	data = db.TextProperty(required = True)
	created = db.DateTimeProperty(auto_now_add = True)
	last_modified = db.DateTimeProperty(auto_now = True)

def get_today_release(today):
	key = today
	logging.error(today)
	releases = memcache.get(key)
	if releases is None:
		logging.error('DB QUERY')
		result = db.GqlQuery("SELECT * "
							   "FROM Release "
							   "WHERE created = :1 "
							   "ORDER BY created DESC "
							   "LIMIT 1",
							   datetime.date.today())
		row = result.get()		
		if row:
			logging.error('RELEASE FOUND IN DB')	
			releases = row.data
			memcache.set(key, releases)
		if releases is None:
			logging.error('FETCHING RELEASE API')
			releases = query.query_api()
			r = Release(data = releases)
			r.put()
			memcache.set(key, releases)
	return json.loads(releases)

def get_title(title):
	title_url = urllib2.unquote(title)
	title_url = title_url.replace(' ', '-')
	title = urllib2.quote(title_url.replace('-', ' '))
	key = title_url
	movie = memcache.get(title_url)
	if not movie:
		logging.error('DB QUERY')
		q = db.GqlQuery("SELECT * "
							   "FROM Movie "
							   "WHERE title = :1 "
							   "LIMIT 1",
							   title_url)
		row = q.get()
		if movie:
			logging.error('MOVIE FOUND IN DB')
			movie = row.data
			memcache.set(key, movie)
		if not movie:
			logging.error('FETCHING MOVIE FROM API')
			movie = query.query_movie(title)
			m_dict = json.loads(movie)
			if m_dict['movies'] != []:
				m = Movie(title = title_url, data = movie)
				m.put()
				memcache.set(key, movie)
			else:
				movie = '{}'
	return json.loads(movie)


app = webapp2.WSGIApplication([
					('/', MainPage),
					('/search_magnet.json', SearchMagnet),
					('/movie/([a-zA-Z0-9-]+)', MoviePermalink),
					], debug=True)
 				 		