import asab
from .service import ImagePublisherService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class ImagePublisherModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ImagePublisherService(app, "visualizer.ImagePublisherService")

	async def initialize(self, app):
		L.warning("\n[%s] Initialize ImagePublisherModule." % get_current_time())
