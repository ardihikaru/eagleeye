import asab.web.session
from scheduler.zmq import ZMQModule
from scheduler.resizer import ResizerModule
from scheduler.extractor import ExtractorModule
from scheduler.reader import ReaderModule
from mongoengine import connect
from ext_lib.utils import get_current_time


class SchedulerService(asab.Application):

	def __init__(self):
		super().__init__()

		# Connect Database
		connect('eagleeyeDB')
		
		# Add reader module
		self.add_module(ZMQModule)
		self.add_module(ResizerModule)
		self.add_module(ExtractorModule)
		self.add_module(ReaderModule)

		# Initialize reader service
		self.ReaderService = self.get_service("scheduler.ReaderService")

	async def initialize(self):
		print("\n[%s] Scheduler Service is running!" % get_current_time())
		# Start subscription
		await self.ReaderService.start_subscription()
