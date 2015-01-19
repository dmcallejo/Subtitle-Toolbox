#!/usr/bin/python
# -*- coding: utf-8 -*-

import sites.subtitulos_es
import urllib2
import sys,math,getopt,re
reload(sys)
sys.setdefaultencoding('utf8')


def main(argv):
	video_file = None
	tvseries = None
	season = None
	episode = None
	try:
		opts, args = getopt.getopt(argv,"hf:t:s:e:",["test","tvseries=","season=","episode=","file="])
	except getopt.GetoptError:
		print 'subtitle_toolbox.py -t <tv-series> -s <season> -e <episode>'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'subtitle_toolbox.py -t <tv-series> -s <season> -e <episode>'
			sys.exit()
		elif opt in ("-f", "--file"):
			video_file=arg
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


def download_by_file(video_file):
	if(video_file.rfind("/")!=-1):
		path,filename = video_file.rsplit("/",1)
	else:
		path=""
		filename=video_file
	season = re.search('(?<=[Ss])[0-9][0-9](?=E[0-9][0-9])',filename).group(0)
	episode = re.search('(?<=S[0-9][0-9]E)[0-9][0-9]',filename).group(0)
	

	print season
	print episode
	print path
	print filename


def test():
	sites.subtitulos_es.get_all_subtitles("Banshee",3,1)

if __name__ == "__main__":
	main(sys.argv[1:])
