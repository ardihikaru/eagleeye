import asab.web.rest
import aiohttp.web
import logging

###

L = logging.getLogger(__name__)


###


class PCSApiWebHandler(object):

	def __init__(self, app):
		self.pcs_api_svc = app.get_service("pcs.PCSApiService")

		app.rest_web_container.WebApp.router.add_post('/pcs', self._post_pcs_data)

	async def _post_pcs_data(self, request):
		try:
			request_json = await request.json()
		except Exception as e:
			L.error("Unable to extract request json")
			raise aiohttp.web.HTTPBadRequest(reason="Unable to extract request json")

		# Submit request
		status, status_code, msg = await self.pcs_api_svc.calculate_pcs_and_wait(
			request_json=request_json,
		)

		# Send back the response
		return asab.web.rest.json_response(request, {
			"status": status,
			"status_code": status_code,
			"data": msg,
		}, status=status)

