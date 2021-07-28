import asab
import logging
import platform
import os
import sys
from .log import Logging, StructuredDataFormatter

asab.Config.add_defaults({
	"customized:log": {
		"enabled": True,

		# disable this to fix the bug when deploy with using docker-compose (ECRCB-348)
		# "format": "%(asctime)s %(levelname)s [%(hostname)s] [%(threadName)s] %(name)s - %(message)s",

		"use_color": True,
		"datefmt": "%Y-%m-%d %H:%M:%S,%f",
	}
})


class HostnameFilter(logging.Filter):
	hostname = platform.node()

	def filter(self, record):
		record.hostname = HostnameFilter.hostname
		return True


class CustomLogging(object):
	def __init__(self):
		self.RootLogger = logging.getLogger()
		self.ConsoleHandler = None

	def set_console_logging(self):
		self.ConsoleHandler = logging.StreamHandler(stream=sys.stderr)
		self.ConsoleHandler.addFilter(HostnameFilter())  # add hostname
		self.ConsoleHandler.setFormatter(StructuredDataFormatter(
			fmt=asab.Config["customized:log"].get("format", ""),  # use customized data format
			datefmt=asab.Config["customized:log"]["datefmt"],
			use_color=asab.Config["customized:log"].getboolean("use_color")
		))
		self.ConsoleHandler.setLevel(logging.DEBUG)
		self.RootLogger.addHandler(self.ConsoleHandler)
