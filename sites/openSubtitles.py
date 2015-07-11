#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
import configuration_manager as cm
import utils
import gzip

os_client = OpenSubtitles()
token = None

def get_all_subtitles(path,filename):
	if(token==None):
		login()
	f = File(os.path.join(path,filename))
	hash = f.get_hash()
	size = f.size
	data = os_client.search_subtitles([{'sublanguageid': 'all', 'moviehash': hash, 'moviebytesize': size}])
	return data

def download_subtitles(subtitle_array,path,filename):
	for e in subtitle_array:
		download_subtitle(e,path,filename)

def download_subtitle(element,path,filename):
	# Downloading
	gz_file_path = os.path.join(path,element['SubFileName']+'.gz')
	srt_file_path = os.path.join(path,filename)+'.'+element['SubLanguageID']+'.'+element['SubFormat']
	utils.download_file(element['SubDownloadLink'],gz_file_path)
	# Subtitle extraction
	inF = gzip.open(gz_file_path, 'rb')
	outF = open(srt_file_path, 'wb')
	outF.write(inF.read())
	inF.close()
	outF.close()
	print "Downloaded",srt_file_path
	os.remove(gz_file_path)



# Login functions

def login():
	configuration_manager=cm.Configuration_Manager()
	token = os_client.login(configuration_manager.openSubtitles.username, configuration_manager.openSubtitles.password)
	print "Logged in."

def logout():
	os_client.logout()
	token=None
