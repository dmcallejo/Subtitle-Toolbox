#!/usr/bin/python3
# -*- coding: utf-8 -*-

import sites.subtitulos_es
import sites.openSubtitles
import sites.tvdb
import configuration_manager as cm
import math,getopt,re
import utils
import iso6392
import shutil,os,sys
from subprocess import call
from classes import *
import string

configuration = None

def main(argv):
	video_file = None
	tvseries = None
	season = None
	episode = None
	try:
		opts, args = getopt.getopt(argv,"hf:t:s:e:o:",["test","tvseries=","season=","episode=","file="])
	except getopt.GetoptError:
		print('subtitle_toolbox.py -t <tv-series> -s <season> -e <episode>')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('subtitle_toolbox.py -t <tv-series> -s <season> -e <episode>')
			sys.exit()
		elif opt in ("-f", "--file"):
			video_file=arg.strip()
			break
		elif opt in ("-t", "--tvseries"):
			tvseries = arg
			continue
		elif opt in ("-s", "--season"):
			season = int(arg)
		elif opt in ("-e", "--episode"):
			episode = int(arg)
		elif opt in ("--test"):
			test()
			exit(0)

	if(video_file!=None):
		download_by_file(video_file)
		exit(0)
	if(tvseries==None):
		print("No series specified.")
		sys.exit(2)
	elif(season==None or math.isnan(season)):
		print("No season specified.")
		sys.exit(2)
	elif(episode==None or math.isnan(episode)):
		print("No season specified.")
		sys.exit(2)

	sites.subtitulos_es.get_all_subtitles(tvseries,season,episode)
	exit(0)

def upload_subtitles(subtitle_files,movie_file):
	sites.openSubtitles.upload_subtitles(subtitle_files,movie_file)

def download_by_file(video_file,output="../"):
	if(video_file.rfind("/")!=-1):
		path,filename = video_file.rsplit("/",1)
	else:
		path=""
		filename=video_file

	series,season,episode_number,info = parse_filename(filename)
	tvdb = sites.tvdb.tvdb()
	tvdb.get_info(series,season,episode_number)
	
	series,episode_name = sites.openSubtitles.get_episode_info(None,filename,path)

	if episode_name is None:
		print("Error fetching subtitles: No subtitle found.")
		return 1
	episode = Episode(series,season,episode_number,episode_name,path,filename)

	results = search(episode)
	check_languages(results,filename)
	print("Processing: ",episode)
	
	subtitle_args = []
	tmp_path="/tmp/subchecker/"
	if not os.path.exists(tmp_path):
		os.makedirs("/tmp/subchecker/")

	for lang in get_configuration().subtitles.languages:
		data = results[lang]
		srt_file = sites.openSubtitles.download_subtitle(data,tmp_path,filename)
		if not "SubEncoding" in data or data["SubEncoding"] == '':
			print("No SubEncoding field found for",lang,". Enforcing utf-8")
			data["SubEncoding"] = "utf-8"
		subtitle_args +=("--sub-charset", "0:"+data["SubEncoding"], "--language", "0:"+lang, "--track-name", "0:\""+iso6392.get_string(lang)+"\"",srt_file)
	
	#mkvmerge operations
	result = -1
	
	output+="/"+episode.series+"/"+episode.series+" S"+str(season).zfill(2)
	sys.stdout.flush()
	mkvmerge_args = ["mkvmerge","-o", output+"/"+str(episode)+".mkv", "--title", "\""+str(episode)+"\"", "--language", "1:eng", "--track-name", "1:English", path.replace("\\","")+"/"+filename]+subtitle_args
	
	result = call(mkvmerge_args)
	shutil.rmtree(tmp_path)
	return result

def parse_filename(filename):
	#
	# Series.S01.E02.info.mkv case
	#
	if(filename.count('/')>0):
		filename = filename.rsplit('/',maxsplit=1)[1]
	if(re.search('\.S[0-9]{1,2}E[0-9][0-9]\.',filename,flags=re.IGNORECASE)!=None): 
		series = re.search('.+(?=\.[Ss][0-9][0-9])',filename).group(0)
		season = re.search('(?<=[Ss])[0-9]{1,2}(?=[Ee][0-9][0-9]\.)',filename).group(0)
		episode = re.search('(?<=[Ss][0-9][0-9][Ee])[0-9][0-9]',filename).group(0)
		info = re.search('(?<=\.[Ss][0-9][0-9][Ee][0-9][0-9]\.).+(?=\.mkv)',filename)
		if(info!=None):
			info=info.group(0)
	#
	# Series.1x02.info.mkv case
	#
	elif(re.search('\.[0-9]{1,2}x[0-9][0-9]\.',filename,flags=re.IGNORECASE)!=None):
		series = re.search('.+(?=\.[0-9]{1,2}[xX])',filename).group(0)
		season = re.search('(?<=)[0-9]{1,2}(?=[xX][0-9][0-9]\.)',filename).group(0)
		episode = re.search('(?<=[0-9][xX])[0-9][0-9]',filename).group(0)
		info = re.search('(?<=\.[0-9][Xx][0-9][0-9]\.).+(?=\.mkv)',filename)
		if(info!=None):
			info=info.group(0)
	else:
		raise Exception("ERROR parsing filename "+filename)
	if series!=None:
		series=series.replace('.',' ')
		series=series.replace('_',' ')
		series=series.title()
	else:
		raise Exception("ERROR getting series name from "+filename)
	return series,season,episode,info

def get_configuration():
	global configuration
	if(configuration == None):
		configuration = cm.Configuration_Manager()
	return configuration

def search(episode):
	languages = get_configuration().subtitles.languages
	return sites.openSubtitles.get_all_subtitles(episode.path,episode.filename,languages)

def check_languages(search_results,filename):
	""" Checks for every language in the configuration and picks only one of them """
	languages = get_configuration().subtitles.languages
	for lang in languages:
		if lang not in search_results:
			raise Exception("Missing "+lang+" ("+iso6392.get_string(lang)+") subtitle")
		else:
			search_results[lang]=sites.openSubtitles.get_best_subtitle(search_results[lang],filename)


def test():
	path = "/home/pi/WD3/SeriesHD/_Downloads"
	filename = "Mr.Robot.S01E01.PROPER.720p.HDTV.X264-DIMENSION.mkv"
	data = sites.openSubtitles.get_all_subtitles(path,filename,get_configuration().subtitles.languages)
	print(sites.openSubtitles.get_episode_info(data,filename))
	#print(sites.openSubtitles.get_best_subtitle(data["eng"],filename))
	#print(sites.openSubtitles.get_best_subtitle(data["spa"],filename))
	#sites.openSubtitles.download_subtitles(data,path,filename)

if __name__ == "__main__":
	main(sys.argv[1:])

def format_filename(s):
	"""Take a string and return a valid filename constructed from the string.
	Uses a whitelist approach: any characters not present in valid_chars are
	removed. Also spaces are replaced with underscores.
	 
	Note: this method may produce invalid filenames such as ``, `.` or `..`
	When I use this method I prepend a date string like '2009_01_15_19_46_32_'
	and append a file extension like '.txt', so I avoid the potential of using
	an invalid filename.
	
	https://gist.github.com/seanh/93666
	
	"""
	valid_chars = "-_.() %s%s" % (string.ascii_letters, string.digits)
	filename = ''.join(c for c in s if c in valid_chars)
	return filename
