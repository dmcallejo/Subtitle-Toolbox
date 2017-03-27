#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

# Import the os module, for the os.walk function
import os,re
import subtitle_toolbox as st
import transmission_toolbox as tt
import configuration_manager as cm
import time
import sys,getopt
import patoolib
import sites

configuration = None

def main(argv):
	try:
		opts, args = getopt.getopt(argv,"htd",["directory","transmission","test"])
	except getopt.GetoptError:
		print('library_manager.py -t OR library_manager.py -d')
		sys.exit(2)
	for opt, arg in opts:
		if opt == '-h':
			print('library_manager.py -t OR library_manager.py -d')
			sys.exit()
		elif opt in ("-test", "--test"):
			test()
			sys.exit()
		elif opt in ("-t", "--transmission"):
			transmission_mode()
		elif opt in ("-d", "--directory"):
			directory_mode()
			break;

#	get_transmission_toolbox().update_all_torrent_trackers()
	exit(0)

def flush():
	sys.stdout.flush()
def log_start():
	print("------------------------")
	print(time.strftime("%c"))
	print("------------------------")
	flush()
def log_end():
	print("------------------------")
	print(time.strftime("%c"))
	print("------------------------")
	flush()

def get_configuration():
	global configuration
	if(configuration == None):
		configuration = cm.Configuration_Manager()
		st.configuration = configuration
	return configuration

def get_transmission_toolbox():
	return tt.Transmission_toolbox(get_configuration().transmission)

def is_valid_video_file(filename):
	if (re.search('.rar$',filename,flags=re.IGNORECASE) or (re.search('.mkv$',filename,flags=re.IGNORECASE) and re.search('sample',filename,flags=re.IGNORECASE) == None)):
		return True
	else:
		return False

def is_valid_subtitle_file(filename):
	if (re.search('.srt$',filename,flags=re.IGNORECASE)):
		return True
	else:
		return False

def test():
	st.test()

def is_a_tvshow(filename):
	if (re.search('.mkv$',filename,flags=re.IGNORECASE) != None and (re.search('\.S[0-9]{1,2}E[0-9][0-9]\.',filename,flags=re.IGNORECASE)!=None or re.search('\.[0-9]{1,2}x[0-9][0-9]\.',filename,flags=re.IGNORECASE)!=None)):
		return True
	else:
		return False
def torrent_is_an_episode(torrent):
	return(re.search('\.S[0-9]{1,2}E[0-9][0-9]\.',torrent.name,flags=re.IGNORECASE)!=None or re.search('\.[0-9]{1,2}x[0-9][0-9]\.',torrent.name,flags=re.IGNORECASE)!=None)

def transmission_mode():
	log_start()
	tvdb = sites.tvdb.tvdb()
	transmission = get_transmission_toolbox()
	torrents=transmission.get_torrents()
	outputDir = get_configuration().subtitles.output
	for t in torrents:
		print("Torrent",t.name)
		if t.progress==100 and transmission.verify_and_stop(t)==0 and torrent_is_an_episode(t):
			files = t.files()
			video_file = None
			subtitle_files = []
			episode_info = None
			# Video files and subtitle files lookup
			for f in files:
				if(is_valid_video_file(files[f]["name"])):
					series,season,episode_number,info = st.parse_filename(files[f]["name"])
					episode_info = tvdb.get_info(series,season,episode_number)
					video_file = t.downloadDir+"/"+files[f]["name"]
				if(is_valid_subtitle_file(files[f]["name"])):
					subtitle_files.append(t.downloadDir+"/"+files[f]["name"])
			# TODO: check if subtitle file is already uploaded, upload it if not. Merge it into the file.
			status = None
			if(len(subtitle_files)>0 and video_file != None):
				print("Local subtitles found:",subtitle_files)
				if(st.upload_subtitles(subtitle_files,video_file,episode_info) == 0):
					status = process_file(transmission,video_file,outputDir)
				else:
					print("Error uploading subtitles.")
					continue

			elif(video_file != None):
				status = process_file(transmission,video_file,outputDir)
			if (status == 0):
				print("Deleting:",t.name)
				transmission.remove_torrent(t)
		print
	log_end()

def process_file(transmission,video_file,outputDir):
	try:
		return st.download_by_file(video_file,outputDir)
	except Exception as e:
		print("\t",e)

def directory_mode():
	log_start()
	try:
		conf=get_configuration()
		flush()
		# Set the directory you want to start from
		rootDir = conf.subtitles.input
		outputDir = conf.subtitles.output
		transmission = get_transmission_toolbox()

		#Loop control
		loop=True
		while(loop):
			loop=False
			for dirName, subdirList, fileList in os.walk(rootDir):
				for fname in fileList:
					if not (is_valid_file(fname)):
						continue

					if dirName != rootDir:
						query=dirName.replace(rootDir,"")+"/"+fname
					else:
						query=fname
					torrent = transmission.search_torrent_by_file(query)
					
					print(query)

					if torrent==None:
						print("/!\\Torrent not found.")
					else:
						if (torrent.progress!=100 or transmission.verify_and_stop(torrent)!=0):
							continue

					if re.search('.rar$',fname,flags=re.IGNORECASE):
						print("Decompressing rar file:",fname)
						patoolib.extract_archive(dirName+"/"+fname, outdir=rootDir)
						transmission.remove_torrent(torrent)
						print("WARNING: Script will restart to handle extracted files.")
						loop=True

					elif is_a_tvshow(fname):
						flush()
						status = st.download_by_file(dirName+"/"+fname,outputDir)
						if (status == 0 and torrent!=None):
							print("Deleting: ",torrent)
							transmission.remove_torrent(torrent)
						elif (status == 0 and torrent==None):
							print("Deleting file:",dirName+"/"+fname)
							os.remove(dirName+"/"+fname)
						print("\n")
					flush()
	except Exception as e:
		print("\nERROR")
		print(e)
	finally:
		log_end()


if __name__ == "__main__":
	main(sys.argv[1:])
