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

	async def calculate_and_wait(self, request_json):

		mbbox_data, selected_pairs = await self.psc_svc.calc_mbbox(
			bbox_data=request_json["bbox_data"],
			det=request_json["det"],
			names=request_json["names"],
			h=request_json["h"],
			w=request_json["w"],
			c=request_json["c"],
			selected_pairs=request_json["selected_pairs"]
		)

		resp_data = {
			"mbbox_data": mbbox_data,
			"selected_pairs": selected_pairs
		}

		return 200, self.StatusCode.REQUEST_OK.value, resp_data
