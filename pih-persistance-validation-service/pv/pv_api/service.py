import asab
from enum import Enum
from asab import LOG_NOTICE
import logging

###

L = logging.getLogger(__name__)


###


class PVApiService(asab.Service):

	class StatusCode(Enum):
		REQUEST_OK = "request_ok"
		BAD_REQUEST = "request_err_0002"

	class ErrorMessage(Enum):
		BAD_REQUEST = "BAD REQUEST"

	def __init__(self, app):
		super().__init__(app, "pv.PVApiService")

		self.pv_svc = app.get_service("pv.AlgorithmService")

	async def calculate_pv_and_wait(self, request_json):
		label, det_status = await self.pv_svc.validate_mbbox(
			request_json["frame_id"],
			request_json["total_pih_candidates"],
			request_json["period_pih_candidates"],
		)

		resp_data = {
			"label": label,
			"det_status": det_status
		}

		L.log(LOG_NOTICE, "[DRONE={}][FRAME={}] Label={}; Det_status={}".format(
			request_json["drone_id"],
			request_json["frame_id"], label, det_status))

		return 200, self.StatusCode.REQUEST_OK.value, resp_data
