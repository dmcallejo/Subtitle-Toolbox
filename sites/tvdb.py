#!/usr/local/bin/python3
# -*- coding: utf-8 -*-
import tvdb_api
import tvdb_exceptions

class tvdb:
        """ Obtains information from TheTVDatabase  """
        def __init__(self, configuration=None):
                self.t = tvdb_api.Tvdb()


        def get_info(self,series,season,episode):
                print("tvdb: Searching",series,"S"+season+"E"+episode)
                try:
                        search_result = self.t[series][int(season)][int(episode)]
                except tvdb_exceptions.tvdb_episodenotfound as e:
                        print("tvdb: Episode not found:",series,"S"+season+"E"+episode)
                        return None
                #TODO
                print(search_result)

