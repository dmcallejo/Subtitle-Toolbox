#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
from pythonopensubtitles.opensubtitles import OpenSubtitles
from pythonopensubtitles.utils import File,get_md5,get_gzip_base64_encoded
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
	try:
		episode_name = data["MovieName"].rsplit("\"",1)[1].strip()
		series_name = data["MovieName"].split("\"",2)[1].strip()
	except Exception as e:
		print("openSubtitles: unable to get episode info")
		return None,filename
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


# Upload functions

def upload_subtitles(subtitle_files,movie_file,episode_info):
	if(token==None):
		login()
	f = File(movie_file)
	if(movie_file.count('/')>0):
		movie_file =  movie_file.rsplit('/',maxsplit=1)[1]
	movie_hash = f.get_hash()
	movie_size = f.size
	for subtitle in subtitle_files:
		subtitle_md5 = get_md5(subtitle)
		assert type(subtitle_md5) == str

		if(subtitle.count('/')>0):
			subtitle_filename = subtitle.rsplit('/',maxsplit=1)[1]
		else:
			subtitle_filename = subtitle

		params = [{'cd1': [{'submd5hash': subtitle_md5,
				  'subfilename': subtitle,
				  'moviehash': movie_hash,
				  'moviebytesize': movie_size}]}]
		try:
			already_in_db = os_client.try_upload_subtitles(params)
		except Exception as e:
			print("An error ocurred while trying to upload subtitles:",e)
			return 1
		assert type(already_in_db) == bool
		if(already_in_db):
			print("Subtitle already in db")
			continue
		else:
			if(episode_info.episode_imdb_id):
				imdb_id = episode_info.episode_imdb_id
			else:
				print("No episode imdb id found. Using tv show imdb id")
				imdb_id = episode_info.series_imdb_id
			imdb_id = imdb_id.replace("t", "")
			params = {'baseinfo': {'idmovieimdb': imdb_id},
				'cd1': {
				'subhash': subtitle_md5,
				'subfilename': subtitle_filename,
				'moviehash': movie_hash,
				'moviebytesize': movie_size,
				'moviefilename': movie_file,
				'subcontent': get_gzip_base64_encoded(subtitle).decode()}}
			url = os_client.upload_subtitles(params)
			if(url != None):
				print("Subtitle upload succesful!")
			else:
				print("ERROR uploading subtitle.")
				return 1
			return 0
			#assert type(url) == str
			

# Login functions

def login():
	configuration_manager=cm.Configuration_Manager()
	token = os_client.login(configuration_manager.openSubtitles.username, configuration_manager.openSubtitles.password)
	print("Logged in.")

def logout():
	os_client.logout()
	token=None
