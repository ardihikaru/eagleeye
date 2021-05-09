import unittest
import asab
import asyncio
from sorter_service.sorter.frame_id_consumer.service import FrameIDConsumerService
import logging

###

L = logging.getLogger(__name__)


###


class TestFrameIDConsumerService(unittest.TestCase, FrameIDConsumerService):
	""" Testing FrameID Consumer Service """
	def setUp(self):
		""" Set up testing objects """
		self.sorted_seq = [1, 3, 4, 6]
		self.highest_seq_id = 0
		self.highest_seq_id_dropped = 2

	def test_filter_sorted_seq_success_same_result(self):
		filtered_sorted_seq = asyncio.run(self.filter_sorted_seq(self.sorted_seq.copy(), self.highest_seq_id))
		L.warning("[UNITTEST][FrameIDConsumerService][same_result] new sorted seq = `{}`".format(filtered_sorted_seq))
		self.assertTrue(set(filtered_sorted_seq) == set(self.sorted_seq))

	def test_filter_sorted_seq_success_different_result(self):
		filtered_sorted_seq = asyncio.run(self.filter_sorted_seq(self.sorted_seq.copy(), self.highest_seq_id_dropped))
		L.warning("[UNITTEST][FrameIDConsumerService][different_result] new sorted seq = `{}`".format(filtered_sorted_seq))
		self.assertFalse(set(filtered_sorted_seq) == set(self.sorted_seq))


if __name__ == '__main__':
	unittest.main()
