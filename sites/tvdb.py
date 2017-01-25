#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import tvdb_api
import tvdb_exceptions
from classes.Entities import Episode

class tvdb:
        """ Obtains information from TheTVDatabase  """
        def __init__(self, configuration=None):
                self.t = tvdb_api.Tvdb()


        def get_info(self,series,season,episode):
                print("tvdb: Searching",series,"S"+season+"E"+episode)
                try:
                        #Searching for the tv show first
                        search_result = self.t[series]
                
                        series_imdb_id = search_result['imdb_id']

                        #Episode search now
                        search_result = self.t[series][int(season)][int(episode)]

                except tvdb_exceptions.tvdb_shownotfound as e:
                        print("tvdb: tv show not found:",series)
                        return None
                except tvdb_exceptions.tvdb_episodenotfound as e:
                        print("tvdb: Episode not found:",series,"S"+season+"E"+episode)
                        return None
                except tvdb_exceptions.tvdb_error as e:
                        print("tvdb: Unknown API Error:",e)
                        return None
                except Exception as e:
                        print("tvdb: Unknown general error:",e)
                        return None
                episode_name = search_result['episodename']
                episode_imdb_id = search_result['imdb_id']
                episode_info = Episode(series=series,season=season,episode=episode,episode_name=episode_name,series_imdb_id=series_imdb_id,episode_imdb_id=episode_imdb_id)
                print(episode_info)
                return episode_info

