#!/usr/bin/env python3
import asab
import asab.web
import asab.web.rest
from .pcs_api import PCSApiModule
from .candidate_selection import CandidateSelectionModule
from ext_lib.utils import get_current_time
import logging
from dotenv import load_dotenv, find_dotenv

###

L = logging.getLogger(__name__)

###


class PihCandidateSelectionService(asab.Application):
	def __init__(self):
		super().__init__()

		# IMPORTANT: Load `.env` file
		load_dotenv(find_dotenv(filename=asab.Config["commons"]["envfile"]))
		# TODO: Update Dockerfile to COPY `.env` file to container

		# # Testing:
		# import os
		# PYTHONPATH = os.getenv("PYTHONPATH")
		# print(" this is PYTHONPATH:", PYTHONPATH)

		# Web Module
		self.add_module(asab.web.Module)

		# Load web service
		websvc = self.get_service('asab.WebService')

		# Create a private web container
		self.rest_web_container = asab.web.WebContainer(websvc, 'pcs:rest')

		# JSON exception middleware
		self.rest_web_container.WebApp.middlewares.append(asab.web.rest.JsonExceptionMiddleware)

		# Extra Modules
		self.add_module(CandidateSelectionModule)
		self.add_module(PCSApiModule)

	async def initialize(self):
		L.warning('\n[%s] PiH Candidate Selection Service is running!' % get_current_time())
