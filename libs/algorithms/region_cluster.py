from libs.commons.util import find_point
import numpy

class RegionCluster:
    # def __init__(self, img_width, img_height):
    def __init__(self):
        # self.img_width = img_width
        # self.img_height = img_height
        # self.num_regions = 6
        self.num_combination = 11

        # Set pre-defined regions
        # self.clusters = [
        #     [1, 2], [1, 3], [1, 5], # 0-2
        #     [2, 3], [2, 4], [2, 5], [2, 6], # 3-6
        #     [3, 5], [3, 6], # 7-8
        #     [4, 5], # 9
        #     [5, 6] # 10
        # ]
        self.clusters = [
            ["1, 2"], ["1, 3"], ["1, 5"], # 0-2
            ["2, 3"], ["2, 4"], ["2, 5"], ["2, 6"], # 3-6
            ["3, 5"], ["3, 6"], # 7-8
            ["4, 5"], # 9
            ["5, 6"] # 10
        ]
        # region 1 (i=0) is clustered into cluster i={0, 1, 2}
        # region 2 (i=1) is clustered into cluster i={0, 3, 4, 5, 6}
        # region 3 (i=2) is clustered into cluster i={1, 3, 7, 8}
        # region 4 (i=3) is clustered into cluster i={4, 9}
        # region 5 (i=3) is clustered into cluster i={2, 5, 9, 10}
        # region 6 (i=3) is clustered into cluster i={6, 8, 10}
        self.region_xyxy = [
            [[0, 1080, 640, 540], [0, 1, 2]],
            [[640, 1080, 1280, 540], [0, 3, 4, 5, 6]],
            [[1280, 1080, 1920, 540], [1, 3, 7, 8]],
            [[0, 540, 640, 0], [4, 9]],
            [[640, 540, 1280, 0], [2, 5, 9, 10]],
            [[1280, 540, 1920, 0], [6, 8, 10]]
        ]
        self.mapped_obj = []
        for i in range(self.num_combination):
            self.mapped_obj.append({"Person": [], "Flag": []})
            # self.mapped_obj.append([])

    def get_map(self):
        pass


