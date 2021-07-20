#!/usr/bin/env python3
import asab
import asab.web
import asab.web.rest
from .frame_id_consumer import FrameIDConsumerModule
from .algorithm import AlgorithmModule
from latency.module import LatencyCollectorModule
from ext_lib.utils import get_current_time
import logging
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)

###


class SorterApplication(asab.Application):
	def __init__(self):
		super().__init__()

		# IMPORTANT: Load `.env` file
		load_dotenv(find_dotenv(filename=asab.Config["commons"]["envfile"]))
		# TODO: Update Dockerfile to COPY `.env` file to container

		# # Testing:
		# import os
		# PYTHONPATH = os.getenv("PYTHONPATH")
		# print(" this is PYTHONPATH:", PYTHONPATH)

		# Extra Modules
		self.add_module(LatencyCollectorModule)
		self.add_module(AlgorithmModule)
		self.add_module(FrameIDConsumerModule)

	async def initialize(self):
		L.warning('\n[%s] Sorter Service is running!' % get_current_time())
