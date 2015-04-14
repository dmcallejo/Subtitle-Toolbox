#!/usr/bin/python
# -*- coding: utf-8 -*-

import sites.subtitulos_es
import urllib2
import sys,math,getopt,re
import utils
import iso6392
import shutil,os
from subprocess import call
from classes import *
reload(sys)
sys.setdefaultencoding('utf8')
import string

def main(argv):
	video_file = None
	tvseries = None
	season = None
	episode = None
	try:
		opts, args = getopt.getopt(argv,"hf:t:s:e:o:",["test","tvseries=","season=","episode=","file="])
	except getopt.GetoptError:
		print 'subtitle_toolbox.py -t <tv-series> -s <season> -e <episode>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'subtitle_toolbox.py -t <tv-series> -s <season> -e <episode>'
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
		print "No series specified."
		sys.exit(2)
	elif(season==None or math.isnan(season)):
		print "No season specified."
		sys.exit(2)
	elif(episode==None or math.isnan(episode)):
		print "No season specified."
		sys.exit(2)

	sites.subtitulos_es.get_all_subtitles(tvseries,season,episode)
	exit(0)


def download_by_file(video_file,output="../"):
	if(video_file.rfind("/")!=-1):
		path,filename = video_file.rsplit("/",1)
	else:
		path=""
		filename=video_file

	#
	# Series.S01.E02.info.mkv case
	#
	if(re.search('\.S[0-9]{1,2}E[0-9][0-9]\.',filename,flags=re.IGNORECASE)!=None): 
		series = re.search('.+(?=\.[Ss][0-9][0-9])',filename).group(0)
		season = re.search('(?<=[Ss])[0-9]{1,2}(?=[Ee][0-9][0-9]\.)',filename).group(0)
		episode = re.search('(?<=[Ss][0-9][0-9][Ee])[0-9][0-9]',filename).group(0)
		info = re.search('(?<=\.[Ss][0-9][0-9][Ee][0-9][0-9]\.).+(?=\.mkv)',filename).group(0)
	#
	# Series.1x02.info.mkv case
	#
	elif(re.search('\.[0-9]{1,2}x[0-9][0-9]\.',filename,flags=re.IGNORECASE)!=None):
		series = re.search('.+(?=\.[0-9]{1,2}[xX])',filename).group(0)
		season = re.search('(?<=)[0-9]{1,2}(?=[xX][0-9][0-9]\.)',filename).group(0)
		episode = re.search('(?<=[0-9][xX])[0-9][0-9]',filename).group(0)
		info = re.search('(?<=\.[0-9][Xx][0-9][0-9]\.).+(?=\.mkv)',filename).group(0)
	else:
		print "ERROR parsing filename "+filename
		return 1

	if series!=None:
		series=series.replace('.',' ')
		series=series.replace('_',' ')
	else:
		print "ERROR parsing getting series name from "+filename
		return 1

	episode_name = sites.subtitulos_es.get_episode_name(series,season,episode)
	if episode_name is None:
		print "Error fetching subtitles"
		return 1
	episode_subtitles = Episode(series=series,season=season,episode=episode)

	episode_subtitles.releases=search(series,season,episode)
	print series+" - "+episode_name

	subtitle_args = []
	if not os.path.exists("/tmp/subchecker/"):
		os.makedirs("/tmp/subchecker/")

	for idx,release in enumerate(episode_subtitles.releases):
		for idy,subtitle in enumerate(release.subtitles):
			sub_filename = "/tmp/subchecker/"+filename[:-3]+subtitle.language+str(idx)+str(idy)+".srt"
			print "\t>"+str(subtitle).strip()
			utils.download_file(subtitle.url,sub_filename)
			subtitle_args +=("--sub-charset", "0:UTF-8", "--language", "0:"+subtitle.language, "--track-name", "0:\""+iso6392.get_string(subtitle.language)+"\"",sub_filename)

	if not "0:spa" in subtitle_args:
		shutil.rmtree('/tmp/subchecker/')
		return 1

	
	title = format_filename(series+" S"+str(season).zfill(2)+"E"+str(episode).zfill(2)+" - "+episode_name)
	
	output+="/"+series+"/"+series+" S"+str(season).zfill(2)
	mkvmerge_args = ["mkvmerge","-o", output+"/"+title+".mkv", "--title", "\""+title+"\"", "--language", "1:eng", "--track-name", "1:English", path.replace("\\","")+"/"+filename]+subtitle_args
	
	result = call(mkvmerge_args)

	shutil.rmtree('/tmp/subchecker/')
	return result



def search(series,season,episode):
	return sites.subtitulos_es.get_all_subtitles(series,season,episode)

def test():
	sites.subtitulos_es.get_all_subtitles("Banshee",3,1)

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
