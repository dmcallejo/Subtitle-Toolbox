#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the os module, for the os.walk function
import os,re
import subtitle_toolbox as st
import transmission_toolbox as tt
import time
import sys

print "------------------------"
print time.strftime("%c")
print "------------------------"
sys.stdout.flush()
# Set the directory you want to start from
rootDir = '/home/pi/WD3/SeriesHD/_Downloads/'
outputDir = '/home/pi/WD3/SeriesHD/'
transmission = tt.Transmission_toolbox()
for dirName, subdirList, fileList in os.walk(rootDir):
	for fname in fileList:
		if re.search('.mkv$',fname,flags=re.IGNORECASE) != None and re.search('\.S[0-9][0-9]E[0-9][0-9]\.',fname,flags=re.IGNORECASE)!=None and re.search('sample',fname,flags=re.IGNORECASE) == None:
			if dirName != rootDir:
				query=dirName.replace(rootDir,"")+"/"+fname
			else:
				query=fname
			torrent = transmission.search_torrent_by_file(query)
			print query
			if torrent==None:
				print "/!\\Torrent not found."
			elif torrent.status!='stopped':
				if(transmission.check_and_stop(torrent)!=0):
					continue
			status = st.download_by_file(dirName+"/"+fname,outputDir)
			if status== 0 and torrent!=None:
				print "Deleting: ",torrent
				transmission.remove_torrent(torrent)
			print "\n"
		sys.stdout.flush()
transmission.update_all_torrent_trackers()
print "------------------------"
print time.strftime("%c")
print "------------------------"
sys.stdout.flush()
