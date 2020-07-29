import asab
import asab.web
import asab.web.rest
import asab.web.session
from scheduler.extractor import ExtractorModule
from scheduler.reader import ReaderModule
from mongoengine import connect


class EagleEYEWebService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')

		print("Scheduler Service is running!")

		# Add reader module
		self.add_module(asab.web.Module)
		self.add_module(ExtractorModule)
		self.add_module(ReaderModule)

	# async def initialize(self):
		# print("Scheduler Service is running!")
