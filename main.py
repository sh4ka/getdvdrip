import os
import webapp2
import jinja2
import urllib2
import logging
import json
import datetime

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
 				releases = get_today_release(str(today))
 				self.render('front.html', releases = releases)

class SearchMagnet(Handler):
	"""Search function"""
 	def get(self):
 		search = self.request.get('search')
		self.response.headers['Content-Type'] = "application/json"
		output = query.query_torrent(search)
		self.write(json.dumps(output))

class Release(db.Model):
    data = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)
    last_modified = db.DateTimeProperty(auto_now = True)

def get_today_release(today, update = False):
	key = today
	releases = memcache.get(key)
	if not releases or update:
		logging.error('DB QUERY')
		result = db.GqlQuery("SELECT * "
							   "FROM Release "
							   "WHERE created > :1 "
							   "ORDER BY created DESC "
							   "LIMIT 1",
							   datetime.datetime.now() + datetime.timedelta(days=-1))
		result = list(result)
		if len(result) > 0:			
			releases = result[0].data
			memcache.set(key, releases)
		if not releases:
			logging.error('FETCHING RELEASE API')
			releases = query.query_api()
			r = Release(data = releases)
			r.put()
			memcache.set(key, releases)
	return json.loads(releases)

app = webapp2.WSGIApplication([
					('/', MainPage),
					('/search_magnet.json', SearchMagnet)
					], debug=True)
 				 		