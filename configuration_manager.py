#!/usr/bin/python3
# -*- coding: utf-8 -*-

from xml.etree import ElementTree as ET
import classes.Configuration as configuration
import getpass
import os
import iso6392

"""
-----------
XML FORMAT: 
-----------

<?xml version='1.0' encoding='UTF-8'?>
<configuration>
	<transmission>
		<address></address>
		<port></port>
		<auth>
			<login></login>
			<password></password>
		</auth>
	</transmission>
	<subtitles>
		<input></input>
		<output></output>
		<languages></languages>
	</subtitles>
	<accounts>
		<openSubtitles>
			<username></username>
			<password></password>
		</openSubtitles>
	</accounts>
</configuration>

"""



class Configuration_Manager:

	_default_filename = ".transmission_settings.xml"

	def __init__(self,config_file=None):
		if(not config_file):
			config_file = self._default_filename
			os.chdir(os.path.dirname(os.path.realpath(__file__))) 	#	This will prevent relative paths from failing.
																# when executing the script outside the filepath.
		self.transmission=configuration.Transmission_Config()
		self.subtitles=configuration.Subtitles_Config()
		self.openSubtitles=configuration.Account()
		self.load_config(config_file)


	def load_config(self,config_file):
		config_loaded=False
		try:
			file = open(config_file,"r")
			self.config_loaded=True
		except IOError as e:
			print("No settings file. Creating new settings.")
			self.create_config(config_file)
		finally:
			if not config_loaded:
				file = open(config_file,"r")
		try:
			config_file = ET.parse(file)
			config =  config_file.getroot()
			self.transmission.login=config.findall("./transmission/auth/login")[0].text
			self.transmission.password=config.findall("./transmission/auth/password")[0].text
			self.openSubtitles.username=config.findall("./accounts/openSubtitles/username")[0].text
			self.openSubtitles.password=config.findall("./accounts/openSubtitles/password")[0].text
			self.subtitles.languages=['eng']
			for e in config.iter():
				if e.tag=="address":
					self.transmission.address=e.text
				elif e.tag=="port":
					self.transmission.port=e.text
				#elif e.tag=="login" and e.tag=="transmission":
				#	self.transmission.liogin=e.text
				#elif e.tag=="password" and e.tag=="transmission":
				#	self.transmission.password=e.text
				elif e.tag=="input":
					self.subtitles.input=e.text
				elif e.tag=="output":
					self.subtitles.output=e.text
				#elif e.tag=="languages" and e.tag=="..subtitles":
				#	languages = self.parse_languages(e.text)
				#	if(languages==False):
				#		raise Exception("Malformed configuration while parsing languages")
				#	self.subtitles.languages=languages
				#elif e.tag=="username" and e.tag=="openSubtitles":
				#	self.openSubtitles.username=e.text
				#elif e.tag=="password" and e.tag=="openSubtitles":
				#	self.openSubtitles.password=e.text
	
		except e:
			print(e)
			print("Malformed Configuraton. See above...")
			exit(1)



	def create_config(self,config_file):
		from sys import stdin
		print("Type transmission client address without port [localhost]")
		address = stdin.readline().strip()
		print("Type transmission client port [9091]")
		port = stdin.readline().strip()

		if address=="":
			address = "localhost"
		if port=="":
			port="9091"

		print("Type transmission login username [default: None]")
		login = stdin.readline().strip()
		if(login!=""):
			password = getpass.getpass().strip()
		else:
			password=""

		print("Type the input path for the subtitles modules (Where your series are being downloaded) ")
		while(True):
			subtitles_input = stdin.readline().strip()
			if(os.path.isdir(subtitles_input)):
				break
			else:
				print("Invalid directory. Please try again:")

		print("Type the output path for the prepared MKVs")
		while(True):
			subtitles_output = stdin.readline().strip()
			if(os.path.isdir(subtitles_output)):
				break
			else:
				print("Invalid directory. Please try again:")

		print("Type the languages the subtitles module should download sepparated by comas. Example: eng,spa,ita. [default: eng]")
		while(True):
			languages = stdin.readline().strip()
			tmp = None
			if(languages==""):
				languages="eng"
			try:
				tmp = self.parse_languages(languages)
				if(tmp==False):
					raise Exception("Invalid input")
			except Exception as e:
				tmp = None
				print(e)
				print("Invalid input. Try again... Example: eng,spa,ita")
			if(tmp!=None):
				print(" - Selected languages: ")
				for e in tmp:
					print(" > ",iso6392.get_string(e))
				break


		print("Type your OpenSubtitles account name [default: No account]")
		os_user = stdin.readline().strip()
		if(os_user!=""):
			os_password = getpass.getpass().strip()



		print("Creating configuration file...")
		#Element tree structure:
		configuration_root = ET.Element("configuration")
		xml_transmission 				= ET.SubElement(configuration_root,"transmission")
		xml_transmission_address 		= ET.SubElement(xml_transmission,"address")
		xml_transmission_port			= ET.SubElement(xml_transmission,"port")
		xml_transmission_auth 			= ET.SubElement(xml_transmission, "auth")
		xml_transmission_auth_login		= ET.SubElement(xml_transmission_auth,"login")
		xml_transmission_auth_password	= ET.SubElement(xml_transmission_auth,"password")

		#Subtitles configuration
		xml_subtitles 			= ET.SubElement(configuration_root,"subtitles")
		xml_subtitles_input 	= ET.SubElement(xml_subtitles,"input")
		xml_subtitles_output	= ET.SubElement(xml_subtitles,"output")
		xml_subtitles_languages	= ET.SubElement(xml_subtitles,"languages")

		#Accounts configuration
		xml_accounts			= ET.SubElement(configuration_root,"accounts")


		# Write of data:
		xml_transmission_address.text = address
		xml_transmission_port.text 	  = port
		xml_transmission_auth_login.text	= login
		xml_transmission_auth_password.text = password

		xml_subtitles_input.text  	 = subtitles_input
		xml_subtitles_output.text 	 = subtitles_output
		xml_subtitles_languages.text = languages

		#Open Subtitles account:
		if(os_user!=""):
			xml_accounts_openSubtitles		= ET.SubElement(xml_accounts,"openSubtitles")
			xml_accounts_openSubtitles_user	= ET.SubElement(xml_accounts_openSubtitles,"username")
			xml_accounts_openSubtitles_pass	= ET.SubElement(xml_accounts_openSubtitles,"password")

			xml_accounts_openSubtitles_user.text  = os_user
			xml_accounts_openSubtitles_pass.text  = os_password

		tree = ET.ElementTree(configuration_root)
		tree.write(config_file,xml_declaration=True,encoding='utf-8')

	def parse_languages(self,languages):
		""" Parses a languages string sepparated by comas """
		if(languages==None):
			print("No languages found")
			return False
		parsed = []
		languages_list = languages.split(',')
		for e in languages_list:
			if(iso6392.get_string(e.strip())==None):
				print("Unrecognized language:",e)
				raise Exception("Unrecognized language:",e)
			parsed.append(e.strip())
		return parsed
