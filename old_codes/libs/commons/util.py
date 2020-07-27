
def find_point(xyxy, xy):
    # if (x1 < x < x2 and
    #         y1 < y < y2):
    if (xyxy[0] < xy[0] < xyxy[2] and
            # xyxy[1] < xy[1] < xyxy[3]):
            xyxy[3] < xy[1] < xyxy[1]):
        return True
    else:
        return False

# # find point
# xyxy = [1280, 1080, 1920, 540]
# xy = [1337.0, 786.0]
# print(" FIND POINT?", find_point(xyxy, xy))

# # get_centroid_xy
# xyxy = [700, 500, 1000, 100]
# xyxy = [777, 545, 1240, 161]
# centroid = get_centroid_xy(xyxy)
# print("--- centroid = ", centroid)


import numpy
# mapped_obj = numpy.zeros(shape=(11, 1), dtype=int)
# mapped_obj = numpy.empty((0, 3), int)
# mapped_obj = numpy.append(mapped_obj, numpy.array([[1, 2, 3]]), axis=0)

# mapped_obj = []
# for i in range(11):
#     mapped_obj.append([])
#
# print(mapped_obj)

# from math import radians, cos, sin, asin, sqrt
#
# def haversine(lat1, lon1, lat2, lon2):
#
#       R = 3959.87433 # this is in miles.  For Earth radius in kilometers use 6372.8 km
#
#       dLat = radians(lat2 - lat1)
#       dLon = radians(lon2 - lon1)
#       lat1 = radians(lat1)
#       lat2 = radians(lat2)
#
#       a = sin(dLat/2)**2 + cos(lat1)*cos(lat2)*sin(dLon/2)**2
#       c = 2*asin(sqrt(a))
#
#       # return R * c
#       return c

# Usage
# lon1 = -103.548851
# lat1 = 32.0004311
# lon2 = -103.6041946
# lat2 = 33.374939

# lon1 = (-1) * 1206.0
# lat1 = 696.0
#
# lon2 = (-1) * 1241.5
# lat2 = 1043.0
#
# lon3 = (-1) * 953.5
# lat3 = 799.0

# # FRAME-9 - OK expected Person-0
# lon1 = (-1) * 1138.0
# lat1 = 665.0
#
# lon2 = (-1) * 1128.5
# lat2 = 1077.5
#
# lon3 = (-1) * 985.5
# lat3 = 702.0

# FRAME-6 -- expected Person-1
# lon1 = 1337.0
# lat1 = 786.0
#
# lon2 = 952.5
# lat2 = 755.5
#
# lon3 = 1164.5
# lat3 = 1053.5


# print("Flag-2 ke Person-0", haversine(lat1, lon1, lat2, lon2))
# print("Flag-2 ke Person-1", haversine(lat1, lon1, lat3, lon3))

# Point to circle: https://www.geeksforgeeks.org/shortest-distance-between-a-point-and-a-circle/

# # Frame-6 -- expected Person-1 - OK
# flag_c = [1337.0, 786.0]
# person_0c = [952.5, 755.5]
# person_1c = [1164.5, 1053.5]
#
# # # Frame-9 -- expected Person-0
# # flag_c = [1138.0, 665.0]
# # person_0c = [1128.5, 1077.5]
# # person_1c = [985.5, 702.0]
#
# from scipy.spatial import distance
#
# print("Flag-2 ke Person-0: ", distance.cityblock(flag_c, person_0c))
# print("Flag-2 ke Person-1: ", distance.cityblock(flag_c, person_1c))

# https://github.com/thinkphp/manhattan-distance/blob/master/manhattan-distance.py