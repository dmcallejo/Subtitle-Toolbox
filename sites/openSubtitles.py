#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File
import configuration_manager as cm
import utils
import gzip
import re

os_client = OpenSubtitles()
token = None

def get_all_subtitles(path,filename,languages=['all']):
	if(token==None):
		login()
	f = File(os.path.join(path,filename))
	hash = f.get_hash()
	size = f.size
	data = {}
	for lang in languages:
		result = os_client.search_subtitles([{'sublanguageid': lang, 'moviehash': hash, 'moviebytesize': size}])
		if(result):
			data[lang] = result
	return data

def download_subtitles(subtitle_array,path,filename):
	for e in subtitle_array:
		download_subtitle(e,path,filename)

def download_subtitle(element,path,filename):
	""" Downloads an openSubtitle subtitle and returns its path """
	# Downloading
	if re.search('.+(?=\.mkv)',filename):
		filename=re.search('.+(?=\.mkv)',filename).group(0)
	gz_file_path = os.path.join(path,element['SubFileName']+'.gz')
	srt_file_path = os.path.join(path,filename)+'.'+element['SubLanguageID']+'.'+element['SubFormat']
	utils.download_file(element['SubDownloadLink'],gz_file_path)
	# Subtitle extraction
	inF = gzip.open(gz_file_path, 'rb')
	outF = open(srt_file_path, 'wb')
	outF.write(inF.read())
	inF.close()
	outF.close()
	os.remove(gz_file_path)
	return srt_file_path

def get_episode_info(data,filename,path=None):
	if(data==None and path!=None):
		data = get_all_subtitles(path,filename,languages=["eng"])
	if not data:
		return None,None
	if 'eng' in data:
		data = data['eng']
	if (len(data)>1):
		data = get_best_subtitle(data,filename)
	if isinstance(data,list):
		data = data[0]
	episode_name = data["MovieName"].rsplit("\"",1)[1].strip()
	series_name = data["MovieName"].split("\"",2)[1].strip()
	return series_name,episode_name

def get_best_subtitle(data_array,filename):
	match = get_filename_match(data_array,filename)
	if(len(match)>1):
		data_array = match
	highest = get_best_rated(data_array)
	return highest

def get_filename_match(data_array,filename):
	match = re.search('.+(?=\.mkv)',filename).group(0)
	elements = []
	for e in data_array:
		if(utils.similar(e["MovieReleaseName"],match)>0.6):
			elements.append(e)
	return elements

def get_best_rated(data_array):
	highest = None
	for e in data_array:
		if(highest == None or float(e["SubRating"])>float(highest["SubRating"])):
			highest = e
	return highest


# Login functions

def login():
	configuration_manager=cm.Configuration_Manager()
	token = os_client.login(configuration_manager.openSubtitles.username, configuration_manager.openSubtitles.password)
	print "Logged in."

def logout():
	os_client.logout()
	token=None
