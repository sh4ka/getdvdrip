import hashlib
import datetime

import configuration
import salt

def set_cookie(app, param, value, expires='never'):
	cookie = param+'=' + encode_value(value)
	if expires == 'never':
		cookie += '; Expires=Thu, 01-Jan-2050 00:00:00 GMT;'
	app.response.headers.add_header('Set-cookie', cookie)

def get_cookie(app, param):
	encoded_param = app.request.cookies.get(param, None)
	result = None
	if encoded_param is not None:
		param_a, param_b = encoded_param.split('|')
		if param_b == get_encoded_value(param_a):
			result = param_a
	return result

def encode_value(value):
	value = value + '|' + get_encoded_value(value)
	return value

def get_encoded_value(value):
	return hashlib.sha1(salt.SALT+value).hexdigest()