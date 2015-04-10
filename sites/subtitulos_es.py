#!/usr/bin/python
# -*- coding: utf-8 -*-
import utils
import iso6392
import re
from classes import *
from bs4 import BeautifulSoup

URL = "http://www.subtitulos.es/"

def get_all_subtitles(series,season,episode):
	series_url_name = __translate_series_name(series)
	subtitles_url = URL+series_url_name+"/"+str(season)+"x"+str(episode)
	soup = utils.get_soup_from_URL(subtitles_url,debug=False)

	if soup==None:
		return None;

	releases = soup.find_all(id="version")
	subtitle_releases = []
	for release in releases:
		version = __get_release(release)
		subtitles = __get_subtitles_from_release(release)
		subtitle_releases.append(subtitles)
	return subtitle_releases



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

def get_episode_name(series,season,episode):
	series_url_name =  __translate_series_name(series)
	subtitles_url = URL+series_url_name+"/"+str(season)+"x"+str(episode)
	soup = utils.get_soup_from_URL(subtitles_url,debug=False)	
	if soup is None:
		return None
	cabecera_subtitulo = soup.find(id="cabecera-subtitulo")
	nombre = re.search('(?<=x[0-9][0-9] - ).+',cabecera_subtitulo.string)
	if nombre!= None:
		return nombre.group(0)
	else:
		return ""



#########################
#	Internal methods	#
#########################


def __get_release(release_tag):
	for s in release_tag.p.strings:
		if "versión" in s.lower():
			tmp =  s.split(" ")[1:-2]
			" ".join(tmp)
			return " ".join(tmp)

def __get_subtitles_from_release(release_tag):
	#subtitles = {}
	subtitles = SubtitleRelease(__get_release(release_tag))
	for language in release_tag.find_all(class_="li-idioma"):
		raw_href = language.parent.next_sibling.next_sibling
		if(__get_class_as_string(raw_href['class'])!="descargar green"):
			continue
		subtitle = Subtitle(translate_language_to_iso6392(language.strong.string),__get_most_updated_subtitle(raw_href))
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

def __translate_series_name(name):
	name = name.replace(" ","-")
	if(show_name.has_key(name.lower())):
		name = show_name[name.lower()]
	return name


	## SHOW NAME CORRECTIONS ## 
show_name = {'house-of-cards-2013' 	: 'House-of-Cards-(2013)',
		 'transporter-the-series' 	: 'Transporter:-The-Series',
		 'faking-it-2014'			: 'Faking-It'
	}