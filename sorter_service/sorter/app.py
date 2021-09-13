#!/usr/bin/env python3
import asab
import asab.web
import asab.web.rest
from .frame_id_consumer import FrameIDConsumerModule
from .algorithm import AlgorithmModule
from latency.module import LatencyCollectorModule
from ext_lib.utils import get_current_time
import logging
from missing_asab_components.application import Application
import os.path
from dotenv import load_dotenv, find_dotenv
from asab.log import LOG_NOTICE

###

L = logging.getLogger(__name__)

###


class SorterApplication(Application):
	def __init__(self):
		# IMPORTANT: Load `.env` file in this directory (if any)
		# Currently it is used for local deployment, Dockfile may not COPY this `.env` into the container yet
		if os.path.isfile(".env"):
			load_dotenv(find_dotenv())

		super().__init__()

		# Extra Modules
		self.add_module(LatencyCollectorModule)
		self.add_module(AlgorithmModule)
		self.add_module(FrameIDConsumerModule)

	async def initialize(self):
		L.warning('\n[%s] Sorter Service is running!' % get_current_time())
