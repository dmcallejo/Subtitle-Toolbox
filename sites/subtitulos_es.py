#!/usr/bin/python
# -*- coding: utf-8 -*-
import utils
import iso6392
from classes import *
from bs4 import BeautifulSoup

URL = "http://www.subtitulos.es/"

def get_all_subtitles(series,season,episode):
	series_url_name = series.replace(" ","-")
	subtitles_url = URL+series_url_name+"/"+str(season)+"x"+str(episode)
	soup = utils.get_soup_from_URL(subtitles_url,debug=False)

	releases = soup.find_all(id="version")
	for release in releases:
		version = __get_release(release)
		subtitles = __get_subtitles_from_release(release)

		print subtitles


def translate_language_to_iso6392(language):
	if language=="Español (España)" or language=="Español" :
		return iso6392.get_iso6392("Spanish; Castilian")
	elif language=="Català":
		return iso6392.get_iso6392("Catalan; Valencian")
	elif language=="Español (Latinoamérica)":
		return iso6392.get_iso6392("Latin")
	elif language=="English":
		return iso6392.get_iso6392("English")
	elif language=="English":
		return iso6392.get_iso6392("English")
	elif language=="Galego":
		return iso6392.get_iso6392("Galician")



def test():
	get_all_subtitles("Banshee",3,1)


#########################
#	Internal methods	#
#########################

def __get_release(release_tag):
	for s in release_tag.p.strings:
		if "versión" in s.lower():
			return s.split(" ",2)[1].strip()

def __get_subtitles_from_release(release_tag):
	#subtitles = {}
	subtitles = SubtitleRelease(__get_release(release_tag))
	for language in release_tag.find_all(class_="li-idioma"):
		raw_href = language.parent.next_sibling.next_sibling
		if(__get_class_as_string(raw_href['class'])!="descargar green"):
			continue
		subtitle = Subtitle(language.strong.string,__get_most_updated_subtitle(raw_href))
		subtitles.add(subtitle)


		#subtitles[language.strong.string]=__get_most_updated_subtitle(raw_href)

	return subtitles

	# Utils #
def __get_class_as_string(class_set):
	ret = ""
	for e in class_set:
		ret+= e +" "
	return ret.strip()

def __get_most_updated_subtitle(raw_href):
	a = raw_href.find_all("a")
	[s for s in a if "updated" in s['href']]
	return s['href']	#Somewhat if there's no updated one, it will return the only available.