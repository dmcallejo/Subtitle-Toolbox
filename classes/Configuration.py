#!/usr/bin/python
# -*- coding: utf-8 -*-

class Transmission_Config:
	""" Stores Transmission config """
	def __init__(self):
		self.address=None
		self.port=None
		self.login=None
		self.password=None

class Subtitles_Config:
	""" Stores subtitles management config """
	def __init__(self):
		self.input=None
		self.output=None
		self.languages=[] #TODO: preferred languages
