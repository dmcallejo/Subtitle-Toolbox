#!/usr/bin/python
# -*- coding: utf-8 -*-

import urllib2
import imp
import os
from bs4 import BeautifulSoup

def get_page_from_URL(url,debug=False):
	try:
		req = urllib2.Request(url, headers={'User-Agent' : "Magic Browser"}) 
		response = urllib2.urlopen(req,timeout=10)
	except urllib2.URLError, e:
		print "Error getting ",url
		print e
		return None
	if(debug):
		print "DEBUG: ",response
	return response.read()

def sanitize_show_name(show,debug=False):
	show = show.replace(" ","-")
	show = show.strip()
	if(debug):
		print "DEBUG: Sanitized show name: ",show

def get_soup_from_URL(url,debug=False):
	return BeautifulSoup(get_page_from_URL(url,debug=False))



MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')

def package_contents(package_name):
	file, pathname, description = imp.find_module(package_name)
	if file:
		raise ImportError('Not a package: %r', package_name)
	# Use a set because some may be both source and compiled.
	return set([os.path.splitext(module)[0]
		for module in os.listdir(pathname)
		if module.endswith(MODULE_EXTENSIONS)])