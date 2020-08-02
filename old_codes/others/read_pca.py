# from libs.algorithms.dimension_reduction.pca import PCA
from sklearn.decomposition import PCA

# Disable: RuntimeWarning: invalid value encountered in true_divide
# Source: https://stackoverflow.com/questions/14861891/runtimewarning-invalid-value-encountered-in-divide
import numpy as np
np.seterr(divide='ignore', invalid='ignore')

# import cv2
from matplotlib.image import imread
import time


print(" ... mulai")

# img_path = "data/four0.jpg"
img_path = "data/out1.png"
# img = cv2.imread(img_path)
# img = np.asarray(cv2.imread(img_path))
img = np.asarray(imread(img_path))
print("img SHAPE awal: ", img.shape)

# img_name = "out1.png"
# img_path = "data/5g-dive/57-frames/" + img_name
img_size = 28
len_img = 1
# len_img = 4

print(" total value: ", (1920 * 1080))

# img_data = np.zeros(((img_size ** 2), len_img))
img_data = np.zeros(((6220800), len_img))
print(" img_data SHAPE: ", img_data.shape)
# img_data[:, 0] = np.ravel(img)
# img_data[:, 1] = np.ravel(img)
# img_data[:, 2] = np.ravel(img)
# img_data[:, 3] = np.ravel(img)
for i in range(0, len_img):
    img_ravel = np.ravel(img)
    print(" img_ravel SHAPE: ", img_ravel.shape)
    img_data[:, i] = np.ravel(img)

print("img_path: ", img_path)
# print("img_data: ", img_data)
print("img_data SHAPE: ", img_data.shape)

# Perform PCA Algorithm
timestamp = time.time()
img_data = img_data.T  # Transform data for Dimensional Reduction Process
print("img_data SHAPE new: ", img_data.shape)
n_comp = 2
# pca = PCA(img_data, n_comp)
# pca_images, components = pca.run()
# print("time used to perform PCA: %.7fs" % round((time.time() - timestamp), 2))

# print("Dimension BEFORE and AFTER dimension reduction")
# print(img_data.shape)
# print(pca_images.shape)
# origin = pca.inverse_pca(img_data, n_comp)
# print("origin SHAPE origin: ", origin.shape)


t0 = time.time()
pca = PCA(n_components=1)
pca.fit(img_data)
X_pca = pca.transform(img_data)
print("original shape:   ", img_data.shape)
print("transformed shape:", X_pca.shape)
t_recv = time.time() - t0
print(".. Compression done in (%.5fs) " % t_recv)

import pickle


t0 = time.time()
# pca_baru = PCA(n_components=1)
# X_new = pca_baru.inverse_transform(X_pca)
X_new = pca.inverse_transform(X_pca)

# print("BACK to original shape:   ", X_new.shape)
print("BACK to original shape:   ", X_new.shape)
# plt.scatter(X[:, 0], X[:, 1], alpha=0.2)
# plt.scatter(X_new[:, 0], X_new[:, 1], alpha=0.8)
# plt.axis('equal');
t_recv = time.time() - t0
print(".. INVERSE done in (%.5fs) " % t_recv)





# import numpy as np
# from sklearn import decomposition
# from sklearn import datasets
# from sklearn.cluster import KMeans
# from sklearn.preprocessing import StandardScaler
#
# iris = datasets.load_iris()
# X = iris.data
# y = iris.target
# X = img_data
# print("X SHAPE new: ", X.shape)
#
# scal = StandardScaler()
# X_t = scal.fit_transform(X)
# print("X_t SHAPE new: ", X_t.shape)
#
# pca = decomposition.PCA(n_components=n_comp)
# pca.fit(X_t)
# X_t = pca.transform(X_t)
# print("X_t SHAPE transformed: ", X_t.shape)
#
# # clf = KMeans(n_clusters=2)
# # clf.fit(X_t)
# #
# # scal.inverse_transform(pca.inverse_transform(clf.cluster_centers_))
# # print("X_t SHAPE latest: ", X_t.shape)
