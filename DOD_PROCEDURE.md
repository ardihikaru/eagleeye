# How new algorithm works

## Key files:
1. Scheduler Service
    - scheduler/extractor/service.py
2. Detection Service
    - detection/algorithm/handler.py
- 

## Previous implementation
1. Scheduler Service
    - scheduler/extractor/service.py
        ```
        ...
        async def extract_video_stream(self, config):  # For stream=`STREAM`
            ...
            # send data into Scheduler service through the pub/sub
			# Never send any frame if `test_mode` is enabled (test_mode=1)
			if not bool(int(asab.Config["stream:config"]["test_mode"])):
				t0_publish = time.time()
				L.warning("[%s] Publishing image into Redis channel: %s" % (get_current_time(), node_channel))
				dump_request = json.dumps({"active": True, "algorithm": config["algorithm"], "ts": time.time()})
				pub(self.redis.get_rc(), node_channel, dump_request)
        ...
        def img_listener_v2(self, consumed_data):
        ...
            # send data into Scheduler service through the pub/sub
			# Never send any frame if `test_mode` is enabled (test_mode=1)
			if not bool(int(asab.Config["stream:config"]["test_mode"])):
				t0_publish = time.time()
				L.warning("[%s] Publishing image into Redis channel: %s" % (get_current_time(), node_channel))
                dump_request = json.dumps({"active": True, "algorithm": config["algorithm"], "ts": time.time()})
				pub(self.redis.get_rc(), node_channel, dump_request)
        ...
        ```
2. Detection Service
    - detection/algorithm/handler.py
        ```
        ...
        # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
        image_info = pubsub_to_json(item["data"])
        ...
        # Set default `mbbox_data` and `plot_info` values
        mbbox_data = []
        plot_info = {}
        ...
        if self.cv_out:
            L.warning("\n[%s][%s][%s] Store Box INTO Visualizer Service!" %
                      (get_current_time(), self.node_alias, str(frame_id)))
            t0_plotinfo_saving = time.time()
            drone_id = asab.Config["stream:config"]["drone_id"]
            plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, str(frame_id))
            redis_set(self.rc, plot_info_key, plot_info, expired=10)  # delete value after 10 seconds
            t1_plotinfo_saving = (time.time() - t0_plotinfo_saving) * 1000
            L.warning('\n[%s] Latency of Storing Plot info in redisDB (%.3f ms)' %
                    (get_current_time(), t1_plotinfo_saving))           
        ```

## Current implementation
1. Scheduler Service
    - scheduler/extractor/service.py
        ```
        ...
        def img_listener_v2(self, consumed_data):
        ...
            # send data into Scheduler service through the pub/sub
			# Never send any frame if `test_mode` is enabled (test_mode=1)
			if not bool(int(asab.Config["stream:config"]["test_mode"])):
				t0_publish = time.time()
				L.warning("[%s] Publishing image into Redis channel: %s" % (get_current_time(), node_channel))

				# TODO: enrich with drone ID information
				dump_request = json.dumps({
					"active": True,
					"algorithm": _config["algorithm"],
					"ts": time.time(),
					"drone_id": img_info["id"],
				})
      
				pub(self.redis.get_rc(), node_channel, dump_request)
        ...
        ```
2. Detection Service
    - detection/algorithm/handler.py
        ```
        ...
        # TODO: To tag the corresponding drone_id to identify where the image came from (Future work)
        image_info = pubsub_to_json(item["data"])
        ...
        # Set default `mbbox_data` and `plot_info` values
        mbbox_data = []
        plot_info = {}
        ...
        # If enable visualizer, send the bbox into the Visualizer Service
		if self.cv_out:
			# Send processed frame info into sorter
			# build channel
			sorter_channel = "{}_{}".format(
				self.ch_prefix,
				str(image_info["drone_id"]),
			)
			# build frame sequence information
			frame_seq_obj = {
				"drone_id": int(image_info["drone_id"]),
				"frame_id": int(frame_id),
				"mbbox_data": mbbox_data,
			}
			pub(self.rc, sorter_channel, json.dumps(frame_seq_obj))

			L.warning("\n[%s][%s][%s] Store Box INTO Visualizer Service!" %
					  (get_current_time(), self.node_alias, str(frame_id)))
			t0_plotinfo_saving = time.time()
			drone_id = asab.Config["stream:config"]["drone_id"]
			plot_info_key = "plotinfo-drone-%s-frame-%s" % (drone_id, str(frame_id))
			redis_set(self.rc, plot_info_key, plot_info, expired=10)  # delete value after 10 seconds
			t1_plotinfo_saving = (time.time() - t0_plotinfo_saving) * 1000
			L.warning('\n[%s] Latency of Storing Plot info in redisDB (%.3f ms)' %
					  (get_current_time(), t1_plotinfo_saving))  
        ```
3. Sorter Service
    - frame_seq_consumer/service.py (**Redis Consumer**)
    ```
    ...
    async def start_subscription(self):
		consumer = self.rc.pubsub()
		consumer.subscribe([self.channel])
		for item in consumer.listen():
			if isinstance(item["data"], int):
				L.warning("\n[{}] Starting subscription to channel `{}_{}`".format(
						  get_current_time(), self.ch_prefix, self.sorter_id
				))
			else:
				frame_seqs = pubsub_to_json(item["data"])
    ...
    ```