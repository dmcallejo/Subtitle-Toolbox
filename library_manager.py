#!/usr/bin/python
# -*- coding: utf-8 -*-

# Import the os module, for the os.walk function
import os,re
import subtitle_toolbox as st
import transmission_toolbox as tt
import configuration_manager as cm
import time
import sys,getopt
reload(sys)
sys.setdefaultencoding('utf8')
import patoolib

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"htd",["directory","transmission"])
		print opts,args
	except getopt.GetoptError:
		print 'library_manager.py -t OR library_manager.py -d'
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print 'library_manager.py -t OR library_manager.py -d'
			sys.exit()
		elif opt in ("-t", "--transmission"):
			print "Not implemented."
			exit(0)
		elif opt in ("-d", "--directory"):
			directory_mode()
			break;
	exit(0)

def flush():
	sys.stdout.flush()
def log_start():
	print "------------------------"
	print time.strftime("%c")
	print "------------------------"
	flush()
def log_end():
	print "------------------------"
	print time.strftime("%c")
	print "------------------------"
	flush()

def directory_mode():
	log_start()
	try:
		conf=cm.Configuration_Manager()
		sys.stdout.flush()
		# Set the directory you want to start from
		rootDir = conf.subtitles.input
		outputDir = conf.subtitles.output
		transmission = tt.Transmission_toolbox(conf.transmission)

		#Loop control
		loop=True
		while(loop):
			loop=False
			for dirName, subdirList, fileList in os.walk(rootDir):
				for fname in fileList:
					if not (re.search('.rar$',fname,flags=re.IGNORECASE) or (re.search('.mkv$',fname,flags=re.IGNORECASE) and re.search('sample',fname,flags=re.IGNORECASE) == None)):
						continue

					if dirName != rootDir:
						query=dirName.replace(rootDir,"")+"/"+fname
					else:
						query=fname
					torrent = transmission.search_torrent_by_file(query)
					
					print query

					if torrent==None:
						print "/!\\Torrent not found."
					else:
						if (torrent.progress!=100 or transmission.verify_and_stop(torrent)!=0):
							continue

					if re.search('.rar$',fname,flags=re.IGNORECASE):
						print "Decompressing rar file:",fname
						patoolib.extract_archive(dirName+"/"+fname, outdir=rootDir)
						transmission.remove_torrent(torrent)
						print "WARNING: Script will restart to handle extracted files."
						loop=True


					elif re.search('.mkv$',fname,flags=re.IGNORECASE) != None and (re.search('\.S[0-9]{1,2}E[0-9][0-9]\.',fname,flags=re.IGNORECASE)!=None or re.search('\.[0-9]{1,2}x[0-9][0-9]\.',fname,flags=re.IGNORECASE)!=None) and re.search('sample',fname,flags=re.IGNORECASE) == None:
						flush()
						status = st.download_by_file(dirName+"/"+fname,outputDir)
						if (status == 0 and torrent!=None):
							print "Deleting: ",torrent
							transmission.remove_torrent(torrent)
						elif (status == 0 and torrent==None):
							print "Deleting file:",dirName+"/"+fname
							os.remove(dirName+"/"+fname)
						print "\n"
					flush()
			transmission.update_all_torrent_trackers()
	except Exception, e:
		print "\nERROR"
		print e
	finally:
		log_end()


if __name__ == "__main__":
	main(sys.argv[1:])