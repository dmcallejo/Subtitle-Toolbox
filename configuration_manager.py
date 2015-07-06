#!/usr/bin/python
# -*- coding: utf-8 -*-

from lxml import etree as ET
import classes.Configuration as configuration
import getpass
import os

"""
-----------
XML FORMAT: 
-----------

<?xml version="1.0"?>
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
	def __init__(self):
		os.chdir(os.path.dirname(os.path.realpath(__file__))) 	#	This will prevent relative paths to images from failing.
																# when executing the script outside the filepath.
		self.transmission=configuration.Transmission_Config()
		self.subtitles=configuration.Subtitles_Config()
		self.openSubtitles=configuration.Account()
		self.load_config()


	def load_config(self):
		config_loaded=False
		try:
			file = open(".transmission_settings.xml","r")
			self.config_loaded=True
		except IOError, e:
			print "No settings file. Creating new settings."
			self.create_config()
		finally:
			if not config_loaded:
					file = open(".transmission_settings.xml","r")
			config_file = ET.parse(file)
			config =  config_file.getroot()
			for e in config.iter():
				if e.tag=="address":
					self.transmission.address=e.text
				elif e.tag=="port":
					self.transmission.port=e.text
				elif e.tag=="login" and e.getparent().getparent().tag=="transmission":
					self.transmission.login=e.text
				elif e.tag=="password" and e.getparent().getparent().tag=="transmission":
					self.transmission.password=e.text
				elif e.tag=="input":
					self.subtitles.input=e.text
				elif e.tag=="output":
					self.subtitles.output=e.text
				elif e.tag=="username" and e.getparent().tag=="openSubtitles":
					self.openSubtitles.username=e.text
				elif e.tag=="password" and e.getparent().tag=="openSubtitles":
					self.openSubtitles.password=e.text


	def create_config(self):
		from sys import stdin
		print "Type transmission client address without port [localhost]"
		address = stdin.readline().strip()
		print "Type transmission client port [9091]"
		port = stdin.readline().strip()

		if address=="":
			address = "localhost"
		if port=="":
			port="9091"

		print "Type transmission login username [default: None]"
		login = stdin.readline().strip()
		print "Type transmission password [default: None]"
		password = getpass.getpass().strip()

		print "Type the input path for the subtitles modules (Where your series are being downloaded) "
		while(True):
			subtitles_input = stdin.readline().strip()
			if(os.path.isdir(subtitles_input)):
				break
			else:
				print "Invalid directory. Please try again:"

		print "Type the output path for the prepared MKVs"
		subtitles_output = stdin.readline().strip()
		while(True):
			if(os.path.isdir(subtitles_output)):
				break
			else:
				print "Invalid directory. Please try again:"


		print "Type your OpenSubtitles account name [default: No account]"
		os_user = stdin.readline().strip()
		if(os_user!=""):
			os_password = getpass.getpass().strip()



		print "Creating configuration file..."
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

		#Accounts configuration
		xml_accounts					= ET.SubElement(configuration_root,"accounts")


		# Write of data:
		xml_transmission_address.text = address
		xml_transmission_port.text 	  = port
		xml_transmission_auth_login.text	= login
		xml_transmission_auth_password.text = password

		xml_subtitles_input.text  = subtitles_input
		xml_subtitles_output.text = subtitles_output

		#Open Subtitles account:
		if(os_user!=""):
			xml_accounts_openSubtitles		= ET.SubElement(xml_accounts,"openSubtitles")
			xml_accounts_openSubtitles_user	= ET.SubElement(xml_accounts_openSubtitles,"username")
			xml_accounts_openSubtitles_pass	= ET.SubElement(xml_accounts_openSubtitles,"password")

			xml_accounts_openSubtitles_user.text  = os_user
			xml_accounts_openSubtitles_pass.text  = os_password

		tree = ET.ElementTree(configuration_root)
		tree.write(".transmission_settings.xml",pretty_print=True,encoding='utf-8')