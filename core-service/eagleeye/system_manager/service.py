import asab
import time
import logging

###

L = logging.getLogger(__name__)


###


class SystemManagerService(asab.Service):
	"""
	This class manages system messages in within the application
	"""
	def __init__(self, app):
		super().__init__(app, "eagleeye.SystemManagerService")

		self.is_running = True

	async def data_subscriber(self):
		while True:
			time.sleep(1)

	async def publish_error(self, system_code, system_message):
		sys_message_json = {
			"code": system_code,
			"message": system_message
		}
		self.App.PubSub.publish(
			"detection.SystemPubSub.message!",
			sys_message_json=sys_message_json,
			asynchronously=True,
		)

		self.is_running = False

	async def get_system_status(self):
		return self.is_running
