#!/usr/bin/python
# -*- coding: utf-8 -*-

import transmissionrpc
import os,time
import xml.etree.cElementTree as ET
#From update trackers:
from bs4 import BeautifulSoup
from urlparse import urlparse
import urllib2
import re

class Transmission_toolbox:
	def __init__(self,transmission_config):
		""" Constructor for the class. Needs a transmission config object. """
		self.address=transmission_config.address
		self.port=transmission_config.port
		self.login=transmission_config.login
		self.password=transmission_config.password
		self.connect()

	def connect(self):
		""" Connects to the torrent server """
		self.tc = transmissionrpc.Client(self.address, port=self.port,user=self.login,password=self.password)

	def search_torrent_by_file(self,filename):
		""" Finds a torrent containing the given filename """
		for torrent in self.tc.get_torrents():
			files = torrent.files()
			for i in files:
				if files[i]['name'] == filename:
					return torrent

	def get_torrents(self):
		""" Proxy for transmissionrpc original function """
		return self.tc.get_torrents()

	def remove_torrent(self,torrent):
		""" Removes a torrent and its data """
		tId = torrent.id
		self.tc.remove_torrent(tId,delete_data=True)


	def verify_and_stop(self,torrent):
		""" Checks if downloaded data is valid through transmission's own verify data and stops the torrent. Does nothing if already stopped. """
		if (torrent.status=="stopped"):
			return 0

		print "Verifying torrent..."
		self.tc.verify_torrent(torrent.id)
		time.sleep(2)
		torrent.update()
		while(torrent.status=="checking"):
			time.sleep(1)
			torrent.update()
		if(torrent.status=="seeding"):
			torrent.stop()
			print "Torrent stopped."
			return 0
		else:
			print "Corrupted torrent."
			return 1

	def update_all_torrent_trackers(self, ignore_stopped=False):
		""" Goes through every torrent in transmission's list and updates its trackers """
		print "Updating every torrent's trackers..."
		torrent_list = self.tc.get_torrents()
		for t in torrent_list:
			#For each torrent in the list.	
			self.update_torrent_trackers(t)
		print "Updating of every torrent's trackers done."

	def update_torrent_trackers(self,t):
		""" Find new trackers for a torrent and adds them.  """
		current_trackers = []
		for tr in t.trackers:
			current_trackers.append(urlparse(str(tr['announce'])).netloc)  	# We save only the netloc of the tracker 
																			#to compare with the new trackers.
		trackers = get_torrent_trackers(t)
		# Then we compare the current trackers against the ones in torrentz.eu
		if trackers==None: #TODO
			return
		new_trackers =  [x for x in trackers if urlparse(x).netloc not in current_trackers]
		# And update the torrent in transmission:
		if len(new_trackers)>0:
			self.tc.change_torrent(t.id,trackerAdd=new_trackers)
			print t,". Added "+str(len(new_trackers))+" tracker(s)."

def get_torrent_trackers(t):
	""" Obtains a list of trackers from the torrentz website. """
	#Getting torrentz page
	try:
		response = urllib2.urlopen("http://torrentz.eu/"+t.hashString,timeout=30)
	except urllib2.URLError, e:
		print "Torrentz.eu offline. Aborting..."
		print e
		exit()
	soup = BeautifulSoup(response.read())
	for tag in soup.find_all(href=re.compile("announce"),limit=1):
		response = urllib2.urlopen("http://torrentz.eu"+tag.get("href"))
		trackers = parse_uTorrent_trackers(response.read())
		trackers = correct_tracker_urls(trackers)
		return trackers

def parse_uTorrent_trackers(string):
	"""	Receives a uTorrent compatible tracker list and converts it to a list. """
	tracker_list = string.split("\n")
	tracker_list = [value for value in tracker_list if value != ""]	#removes empty strings from the list.
	return tracker_list

def correct_tracker_urls(tracker_list):
	if "http://9.rarbg.com:2710/announce" in tracker_list:
		tracker_list = [e.replace("http://9.rarbg.com:2710/announce","udp://9.rarbg.com:2710/announce") for e in tracker_list]

	return tracker_list

