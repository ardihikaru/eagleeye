# Source: https://github.com/kayoyin/signal-processing/blob/master/dimensionality_reduction.py
import numpy as np

class PCA():
    """
    Perform PCA dimensionality reduction on the input image
    :param img: a numpy array of shape (n_samples, dim_images)
    :param n_components: number of principal components for projection
    :return: image in PCA projection, a numpy array of shape (n_samples, n_components)
    """

    def __init__(self, img, n_comp=2):
        self.img = img
        self.n_comp = n_comp

    def run(self):
        # Compute the covariance matrix
        cov_mat = np.cov(self.img.T)
        print(" .... cov_mat:", cov_mat)

        # Compute the eigenvectors and eigenvalues
        eig_val_cov, eig_vec_cov = np.linalg.eig(cov_mat)

        # Make a list of (eigenvalue, eigenvector) tuples
        eig_pairs = [
            (np.abs(eig_val_cov[i]), eig_vec_cov[:, i]) for i in range(len(eig_val_cov))
        ]

        # Select n_components eigenvectors with largest eigenvalues, obtain subspace transform matrix
        eig_pairs.sort(key=lambda x: x[0], reverse=True)
        eig_pairs = np.array(eig_pairs)
        matrix_w = np.hstack(
            [eig_pairs[i, 1].reshape(self.img.shape[1], 1) for i in range(self.n_comp)]
        )

        # Return samples in new subspace
        return np.dot(self.img, matrix_w), matrix_w

    def inverse_pca(self, pca_img, components):
        """
        Obtain the reconstruction after PCA dimensionality reduction
        :param img: Reduced image, a numpy array of shape (n_samples, n_components)
        :param components: a numpy array of size (original_dimension, n_components)
        :return:
        """
        reconstruct = np.dot(pca_img, components.T).astype(int)
        return reconstruct.reshape(-1, 28, 28)

    def mean_square_error(self, A, B):
        """
        Compute the mean square error between two images
        :param A: a numpy array of shape (self.img_height, img_width)
        :param B: a numpy array of shape (self.img_height, img_width)
        :return: a scalar
        """
        return ((A - B) ** 2).mean()
