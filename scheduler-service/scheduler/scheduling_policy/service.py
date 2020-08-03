import asab
import logging
import imagezmq
import time
from ext_lib.utils import get_current_time
import requests 

###

L = logging.getLogger(__name__)


###


class SchedulingPolicyService(asab.Service):
    """ A service to schedule incoming task (image data) """

    def __init__(self, app, service_name="scheduler.SchedulingPolicyService"):
        super().__init__(app, service_name)
        self.selected_node_id = 0
        self.max_node = 1

        print(" >>>> DEFAULT self.selected_node_id:", self.selected_node_id)

    async def schedule(self, max_node=1, sch_policy="round_robin"):
        self.max_node = max_node
        if sch_policy == "round_robin":
            await self.round_robin()
        else:
            await self.round_robin()

        return self._get_selected_node()

    def _get_selected_node(self):
        return self.selected_node_id

    async def round_robin(self):
        print(" >>>> NOW self.selected_node_id:", self.selected_node_id)
        print("I am using Round-Robin")
        self.selected_node_id += 1
        if self.selected_node_id > self.max_node:
            self.selected_node_id = 0  # Reset
