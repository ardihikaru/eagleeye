import asab
import logging
import time
from ext_lib.redis.my_redis import MyRedis
from ext_lib.utils import pubsub_to_json, get_current_time
# from ..storage import Transaction

###

L = logging.getLogger(__name__)


###

class ReaderHandler(MyRedis):

    def __init__(self, app):
        super().__init__(asab.Config)
        print(" # @ ReaderHandler ...")
        self.ReaderService = app.get_service("ReaderService")
        # app.WebContainer.WebApp.router.add_put('/sync', self.put_transactions)
        # app.WebContainer.WebApp.router.add_get('/transactions', self.get_transactions)

        # Extractor service may not exist at this point
        # This variable will be set up in the init time
        # of ServiceAPIModule
        self.ExtractorService = None

    def start(self):
        print("ReaderHandler try to consume the published data")
        channel = asab.Config["pubsub:channel"]["scheduler"]
        consumer = self.rc.pubsub()
        consumer.subscribe([channel])
        for item in consumer.listen():
            if isinstance(item["data"], int):
                pass
            else:
                # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
                config = pubsub_to_json(item["data"])
                t0_data = config["timestamp"]
                t1_data = (time.time() - t0_data) * 1000
                print('\n #### [%s] Latency for Start threading (%.3f ms)' % (get_current_time(), t1_data))
                # TODO: Saving latency for scheduler:consumer

                print("Once data collected, try extracting data..")
                print(" >>> config:", config)
                if config["stream"]:
                    self.ExtractorService.extract_video_stream(config)
                else:
                    self.ExtractorService.extract_folder(config)

                # Stop watching once
                if "stop" in config:
                    print("### System is interrupted and asked to stop comsuming data.")
                    break

        print("## System is no longer consuming data")

    # async def get_transactions(self, request):
    #     fromDate, toDate = None, None
    #     if request.query:
    #         pattern = re.compile('\A(from=|to=)\d+((&from=|&to=)\d+)?')
    #         if pattern.fullmatch(request.query_string):
    #             fromDate = request.query.get('from', None)
    #             toDate = request.query.get('to', None)
    #         else:
    #             raise aiohttp.web.HTTPBadRequest()
    # 
    #     result_cursor = self.TransactionService.find_transactions(fromDate, toDate)
    # 
    #     result = []
    #     for item in await result_cursor.to_list(length=1000):
    #         result.append(item)
    # 
    #     return asab.web.rest.json_response(request, result)
    # 
    # async def put_transactions(self, request):
    #     # Parse/validate request
    #     try:
    #         transaction = Transaction.from_dict(loads(await request.text()))
    #     except Exception as e:
    #         L.error("put_transactions received a bad request: {}".format(e))
    #         raise aiohttp.web.HTTPBadRequest()
    # 
    #     # Replay transaction
    # 
    #     await self.TransactionService.replay_transaction(transaction)
    # 
    #     # Return OK
    #     return aiohttp.web.HTTPOk()
    # 
    # async def pop_queue(self, request):
    #     if request.identity is None:
    #         raise aiohttp.web.HTTPBadRequest()
    # 
    #     return aiohttp.web.Response(
    #         body=await self.LedgerSyncService.pop_sync_queue(request.identity._id)
    #     )


