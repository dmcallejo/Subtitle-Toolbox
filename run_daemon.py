#!/usr/local/bin/python3
# -*- coding: utf-8 -*-

import sys
import sys,getopt
import configuration_manager as cm
import transmission_toolbox as tb
import argparse
import time

def main(argv):
	args = parse_args(argv)
	daemon = Daemon(config_file=args.config)

class Daemon:
	def __init__(self,config_file=None):
		self.configuration = cm.Configuration_Manager(config_file)
		self.transmission = tb.Transmission_toolbox(self.configuration.transmission)

	def loop(self):
		torrents = None
		while True:
			torrents = self.transmission.get_torrents()
			time.sleep(5)

def parse_args(argv):
	parser = argparse.ArgumentParser(description='Process some integers.')
	parser.add_argument('--config','-c', help='specify a config file')

	args = parser.parse_args()
	return args

if __name__ == "__main__":
	main(sys.argv[1:])
