#!/usr/bin/python
# -*- coding: utf-8 -*-

class Subtitle:
	""" Holds the url and language of a single subtitle. """

	def __init__(self, language,url):
		self.language=language
		self.url=url

	def __str__(self):
		return "Language: "+self.language+"\tURL: "+self.url+"\n"

	def language():
		doc = "The language property."
		def fget(self):
			return self._language
		def fset(self, value):
			self._language = value
		def fdel(self):
			del self._language
		return locals()
	language = property(**language())

	def url():
		doc = "The url property."
		def fget(self):
			return self._url
		def fset(self, value):
			self._url = value
		def fdel(self):
			del self._url
		return locals()
	url = property(**url())

	__repr__=__str__

class SubtitleRelease:
	""" Holds the subtitles (Subtitle) for an episode's release. """

	def __init__(self, release):
		self._subtitles = []
		self.release=release

	def __str__(self):
		string = "Release: " + self.release + "\n"
		for subtitle in self.subtitles:
			string+="\t"
			string += str(subtitle)
		return string

	def release():
		doc = "The release property."
		def fget(self):
			return self._release
		def fset(self, value):
			self._release = value
		def fdel(self):
			del self._release
		return locals()
	release = property(**release())

	def subtitles():
		doc = "The subtitles property."
		def fget(self):
			return self._subtitles
		def fset(self, value):
			self._subtitles = value
		def fdel(self):
			del self._subtitles
		return locals()
	subtitles = property(**subtitles())

	def add(self,subtitle):
		self.subtitles.append(subtitle)

class Episode:
	""" Holds the subtitles (SubtitleRelease) from the several releases of an episode. """

	def __init__(self):
		pass

	def __str__(self):
		string = "Series: "+self.series+" "+"S"+self.season+"E"+self.episode
		for release in releases:
			string += release

		return string

	def series():
		doc = "The series property."
		def fget(self):
			return self._series
		def fset(self, value):
			self._series = value
		def fdel(self):
			del self._series
		return locals()
	series = property(**series())

	def season():
		doc = "The season property."
		def fget(self):
			return self.season
		def fset(self, value):
			self.season = value
		def fdel(self):
			del self.season
		return locals()
	season = property(**season())


	def episode():
		doc = "The episode property."
		def fget(self):
			return self._episode
		def fset(self, value):
			self._episode = value
		def fdel(self):
			del self._episode
		return locals()
	episode = property(**episode())


	def releases():
		doc = "The releases property."
		def fget(self):
			return self._releases
		def fset(self, value):
			self._releases = value
		def fdel(self):
			del self._releases
		return locals()
	releases = property(**releases())