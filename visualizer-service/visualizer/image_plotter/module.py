import asab
from .service import ImagePlotterService
from ext_lib.utils import get_current_time
import logging
from asab import LOG_NOTICE

###

L = logging.getLogger(__name__)


###


class ImagePlotterModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)
		self.Service = ImagePlotterService(app, "visualizer.ImagePlotterService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize ImagePlotterModule." % get_current_time())
