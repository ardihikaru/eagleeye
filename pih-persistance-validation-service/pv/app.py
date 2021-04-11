#!/usr/bin/env python3
import asab
import asab.web
import asab.web.rest
from .pv_api import PVApiModule
from .algorithm import AlgorithmModule
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)

###


class PihPersistanceValidationApplication(asab.Application):
	def __init__(self):
		super().__init__()

		# Web Module
		self.add_module(asab.web.Module)

		# Load web service
		websvc = self.get_service('asab.WebService')

		# Create a private web container
		self.rest_web_container = asab.web.WebContainer(websvc, 'pv:rest')

		# JSON exception middleware
		self.rest_web_container.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

		# Extra Modules
		self.add_module(AlgorithmModule)
		self.add_module(PVApiModule)

	async def initialize(self):
		L.warning('\n[%s] PiH Validation Service is running!' % get_current_time())
