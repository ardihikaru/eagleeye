#!/usr/bin/env python3
import asab
import asab.web
import asab.web.rest
from .frame_id_consumer import FrameIDConsumerModule
from .algorithm import AlgorithmModule
from latency.module import LatencyCollectorModule
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)

###


class SorterApplication(asab.Application):
	def __init__(self):
		super().__init__()

		# Extra Modules
		self.add_module(LatencyCollectorModule)
		self.add_module(AlgorithmModule)
		self.add_module(FrameIDConsumerModule)

	async def initialize(self):
		L.warning('\n[%s] Sorter Service is running!' % get_current_time())
