import asab
from .service import TCPCameraServerService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class TCPCameraServerModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = TCPCameraServerService(app, "scheduler.TCPCameraServerService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize TCPCameraServerModule." % get_current_time())
