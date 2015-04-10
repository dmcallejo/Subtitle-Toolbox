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
	def __init__(self):
		self.address="localhost"
		self.port="9091"
		self.login="pi"
		self.password="raspberry"
		self.connect()

	def load_config(self):
		config_loaded=False
		try:
			file = open(".transmission_settings.xml","r")
			config_loaded=True

		except IOError, e:
			print "No settings file. Creating new settings."
			create_config()
		finally:
			if not config_loaded:
				file = open(".transmission_settings.xml","r")
			config_file = ET.parse(file)
			config =  config_file.getroot()
			for e in config.iter():
				if e.tag=="address":
					self.address=e.text
				elif e.tag=="port":
					self.port=e.text
				elif e.tag=="login":
					self.login=e.text
				elif e.tag=="password":
					self.password=e.text

	def create_config(self):
		from sys import stdin
		print "Type transmission client address without port [localhost]"
		address = stdin.readline().strip()
		print "Type transmission client port [9091]"
		port = stdin.readline().strip()

		if address=="":
			address = "localhost"
		if port=="":
			port="9091"

		print "Type transmission login username [default: None]"
		login = stdin.readline().strip()
		print "Type transmission password [default: None]"
		password = stdin.readline().strip()

		print "Creating configuration file..."
		#Element tree structure:
		transmission_root= ET.Element("transmission")
		xml_address = ET.SubElement(transmission_root,"address")
		xml_port	= ET.SubElement(transmission_root,"port")
		xml_auth 	= ET.SubElement(transmission_root, "auth")
		xml_login	= ET.SubElement(xml_auth,"login")
		xml_password= ET.SubElement(xml_auth,"password")

		# Write of data:
		xml_address.text = address
		xml_port.text 	 = port
		xml_login.text	 = login
		xml_password.text= password

		tree = ET.ElementTree(transmission_root)
		tree.write(".transmission_settings.xml")

	def connect(self):
		self.tc = transmissionrpc.Client(self.address, port=self.port,user=self.login,password=self.password)

	def search_torrent_by_file(self,filename):
		for torrent in self.tc.get_torrents():
			files = torrent.files()
			for i in files:
				if files[i]['name'] == filename:
					return torrent

	def remove_torrent(self,torrent):
		tId = torrent.id
		self.tc.remove_torrent(tId,delete_data=True)


	def check_and_stop(self,torrent):
		""" Checks if downloaded data is valid and stops the torrent """
		print "Verifying torrent..."
		self.tc.verify_torrent(torrent.id)
		torrent=self.tc.get_torrent(torrent.id)
		while(torrent.status=="checking"):
			time.sleep(1)
			torrent=self.tc.get_torrent(torrent.id)
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

