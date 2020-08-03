import asab
from .service import SchedulingPolicyService
from ext_lib.utils import get_current_time


class SchedulingPolicyModule(asab.Module):

	def __init__(self, app):
		super().__init__(app)		
		self.Service = SchedulingPolicyService(app, "scheduler.SchedulingPolicyService")

	async def initialize(self, app):
		print("\n[%s] Initialize SchedulingPolicyModule." % get_current_time())
