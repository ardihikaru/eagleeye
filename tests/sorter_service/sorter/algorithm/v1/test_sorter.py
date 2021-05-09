import unittest
import os
from sorter_service.sorter.algorithm.v1.sorter import Sorter
import logging

###

L = logging.getLogger(__name__)


###


class TestSorter(unittest.TestCase):
	""" Testing Post Action Validator """
	def setUp(self):
		""" Set up testing values """
		self.config = {
			"root_dir": "{}/cn_input_model".format(
				os.path.dirname(os.path.realpath(__file__))
			),
			"max_pool": 4,
		}

		# Comparison input model for 4 input
		self.cn_input_model = [
			"0:1", "2:3",
			"0:2", "1:3",
			"1:2"
		]

		# invalid input model
		self.invalid_cn_input_model = [
			"0:1", "2:3",
			"0:2", "1:3",
			"1:2", 1
		]

		self.unsorted_frame_seq = [2, 4, 1, 5]

	def test_run_success_by_cn_size(self):
		sorter = Sorter(self.config)
		sorter.initialize(self.unsorted_frame_seq, cn_size=4)
		sorter.run()

		sorted_frame_seq = sorter.get_sorted_frame_seq()
		L.warning("[UNITTEST][TestSorter][test_run_success] Sorted sequence: {}".format(sorted_frame_seq))
		self.assertIsNotNone(sorted_frame_seq)

	def test_run_success(self):
		sorter = Sorter(self.config)
		sorter.initialize(self.unsorted_frame_seq, cn_input_model=self.cn_input_model)
		sorter.run()

		sorted_frame_seq = sorter.get_sorted_frame_seq()
		L.warning("[UNITTEST][TestSorter][test_run_success] Sorted sequence: {}".format(sorted_frame_seq))
		self.assertIsNotNone(sorted_frame_seq)

	def test_run_failed(self):
		sorter = Sorter(self.config)
		sorter.initialize(self.unsorted_frame_seq, cn_input_model=self.invalid_cn_input_model)
		sorter.run()

		sorted_frame_seq = sorter.get_sorted_frame_seq()
		L.warning("[UNITTEST][TestSorter][test_run_failed] Sorted sequence: {}".format(sorted_frame_seq))
		self.assertIsNone(sorted_frame_seq)


if __name__ == '__main__':
	unittest.main()
