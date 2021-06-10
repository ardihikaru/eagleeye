import asab
from asab import LOG_NOTICE
from .service import SchedulingPolicyService
from ext_lib.utils import get_current_time
import logging

###

L = logging.getLogger(__name__)


###


class SchedulingPolicyModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = SchedulingPolicyService(app, "offloader.SchedulingPolicyService")

	async def initialize(self, app):
		L.log(LOG_NOTICE, "[%s] Initialize SchedulingPolicyModule." % get_current_time())
