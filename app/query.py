import urllib
import urllib2
import json
import logging

import configuration
import api

def get_moviedb_config():
    query_url = configuration.MOVIE_CONFIG_URL + api.MOVIE_API_KEY
    try:
        u = urllib2.urlopen(query_url)
        result = u.read()
    except Exception, e:
        logging.info('MOVIEDB CONFIG ERROR')
    return result.strip()


def query_api():
    result = {}
    query_url = configuration.DVDRELEASESURL + api.API + configuration.DVDPAGELIMIT
    try:
        u = urllib2.urlopen(query_url)
        result = u.read()
    except Exception, e:
        logging.info('RELEASES API ERROR')
    return result.strip()


def query_movie(title):
    result = {}
    query_url = configuration.MOVIEURL + api.API + configuration.QUERYPARAM + title
    try:
        u = urllib2.urlopen(query_url)
        result = u.read()
    except Exception, e:
        logging.info('ROTTEN TOMATOES API ERROR')
    return result.strip()


def get_movie_poster(title):
    # find movie id
    title = urllib.quote_plus(title)
    poster_image= ''
    search_url = configuration.MOVIE_SEARCH_URL + api.MOVIE_API_KEY + '&query=' + title
    try:
        logging.info('Search url: ' + search_url)
        u = urllib2.urlopen(search_url)
        result = u.read()
        data = json.loads(result.strip())
        movie = data['results'][0]
        if movie:
            data_url = configuration.MOVIE_DATA_URL.replace('{id}', str(movie['id']))
            poster_url = data_url + '?api_key=' + api.MOVIE_API_KEY
            logging.info('Poster url: ' + poster_url)
            u = urllib2.urlopen(poster_url)
            data_result = u.read()
            movie_data = json.loads(data_result.strip())
            poster_image = movie_data['posters'][0]['file_path']
        else:
            logging.info('No movie found')
    except Exception, e:
        logging.error('MOVIESDB API ERROR')
        logging.error(e)
        poster_image = None
    return poster_image


def query_torrent(search):
    result = {}
    if search:
        query_url = configuration.QUERYURL + search
        try:
            u = urllib2.urlopen(query_url)
            result = json.loads(u.read())
        except Exception, e:
            logging.info('SEARCH ERROR')
    return result


def get_magnets(json_result):
    magnet_list = []
    try:
        for movie in json_result['MovieList']:
            item = {'name': movie['MovieTitle'], 'magnet': movie['TorrentMagnetUrl'] + configuration.TRACKERS}
            magnet_list.append(item)
    except Exception, e:
            logging.info('NO RESULTS')
    return magnet_list
