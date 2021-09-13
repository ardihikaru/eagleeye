import asab
from enum import Enum
import logging

###

L = logging.getLogger(__name__)


###


class PCSApiService(asab.Service):

	class StatusCode(Enum):
		REQUEST_OK = "request_ok"
		BAD_REQUEST = "request_err_0002"

	class ErrorMessage(Enum):
		BAD_REQUEST = "BAD REQUEST"

	def __init__(self, app):
		super().__init__(app, "pcs.PCSApiService")

		self.psc_svc = app.get_service("pcs.CandidateSelectionService")

	async def calculate_pcs_and_wait(self, request_json):

		mbbox_data = await self.psc_svc.calc_mbbox(
			# bbox_data=request_json["bbox_data"],  # DEPRECATED: no need to send this data anymore. we use `det` instead
			det=request_json["det"],
			names=request_json["names"],
			h=request_json["h"],
			w=request_json["w"],
			c=request_json["c"],
		)

		# Sending response it optional. It is used for validation purpose ONLY
		resp_data = {
			"mbbox_data": mbbox_data,
		}

		L.warning("[DRONE={}] {}".format(request_json["drone_id"], resp_data))

		return 200, self.StatusCode.REQUEST_OK.value, resp_data
