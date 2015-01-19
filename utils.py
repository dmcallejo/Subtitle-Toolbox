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

def parse_tvseries_filename(file_name):
	""" TODO """
	pass


MODULE_EXTENSIONS = ('.py', '.pyc', '.pyo')

def package_contents(package_name):
	file, pathname, description = imp.find_module(package_name)
	if file:
		raise ImportError('Not a package: %r', package_name)
	# Use a set because some may be both source and compiled.
	return set([os.path.splitext(module)[0]
		for module in os.listdir(pathname)
		if module.endswith(MODULE_EXTENSIONS)])

def download_file(url,file_name):
	u = urllib2.urlopen(url)
	f = open(file_name, 'wb')
	meta = u.info()
	file_size = int(meta.getheaders("Content-Length")[0])
	print "Downloading: %s Bytes: %s" % (file_name, file_size)

	file_size_dl = 0
	block_sz = 8192
	while True:
		buffer = u.read(block_sz)
		if not buffer:
			break

		file_size_dl += len(buffer)
		f.write(buffer)
		status = r"%10d  [%3.2f%%]" % (file_size_dl, file_size_dl * 100. / file_size)
		status = status + chr(8)*(len(status)+1)
		print status,

	f.close()