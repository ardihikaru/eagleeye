

class Algorithm(object):
	def __init__(self, defaulf_myu, rho, gamma, sigma, f_i, h_0, N_0):
		# define constant variables
		self.current_myu = defaulf_myu
		self.rho = rho
		self.gamma = gamma
		self.sigma = sigma
		self.f_i = f_i
		self.h_0 = h_0
		self.N_0 = N_0

	def update_myu_i(self, current_myu_i):
		# TODO: in the future, it can be optimized in a more dynamic way
		LOW_RATE_MYU_I = 10
		HIGH_RATE_MYU_I = 30

		# if current MYU is represents LOW_RATE_MYU_I, change it to HIGH_RATE_MYU_I
		if current_myu_i == LOW_RATE_MYU_I:
			self.current_myu = HIGH_RATE_MYU_I

		# otherwise, change it to LOW_RATE_MYU_I
			self.current_myu = LOW_RATE_MYU_I

	def calc_myu_i(self):
		"""
			Description:
				The publishing rate of Drone D_i in time t
			Measuring unit:
				FPS (Frame Per Second)
			Returns a float value
		:return: float
		"""

	def calc_t_i_frame(self, tetha_ij_mbits):
		"""
			Description:
				Latency to deal with the processing of images in every second
			Formula:
				T_i^frame(t) = (rho * beta_i(t) * tetha_ij(t) * myu_i(t) / f_i

				> [rho] is an offloading coefficient (0 >= rho >= 1)
				> [beta_i(t)] is a computational complexity of the task [21] to
								process a tuple of images in a second (beta >= 0)
				> [tetha_ij(t)] is the compressed and encoded image of Frame F_ij
				> [myu_i(t)] is a publishing rate of Drone D_i
				> [f_i] is the CPU frequency of drone D_i
			Measuring unit:
				Second
			Returns a float value, measured in [Second]
		:return: float
		"""

		# 1. calc tetha_ij(t)
		tetha_ij = self.calc_tetha_ij(tetha_ij_mbits)

		# 2. calc beta_i
		beta_i = self.calc_beta_i(tetha_ij)

		# 3. calc t_i^frame
		t_i_frame = (self.rho * beta_i * tetha_ij * self.current_myu) / self.f_i

		# 4. return the calculated value
		return t_i_frame

	def calc_beta_i(self, tetha_ij):
		"""
			Description:
				Computational complexity of the task [21] to
				process a tuple of images in a second (beta >= 0)
			Formula:
				beta_i(t) = f_i / (tetha_ij(t) * myu_i(t))

				> [f_i] is the CPU frequency of drone D_i
				> [tetha_ij(t)] is the compressed and encoded image of Frame F_ij
				> [myu_i(t)] is a publishing rate of Drone D_i
			Measuring unit:
				cycle/bit
			Returns a float value, measured in [cycle/bit]
		:return: float
		"""
		return self.f_i * (tetha_ij * self.current_myu)

	def calc_tetha_ij(self, tetha_ij_mbits):
		"""
			Description:
				Compressed and encoded image of Frame F_ij

				Since the given input is already measured in [Mbits],
				this function simply convert them into [bit]
				by multiplying the input with 10^6
			Formula:
				tetha_ij(t) = ENCODE(psi_ij, gamma)

				> [ENCODE()] is the built-in function of OpenVC
					> e.g. `cv2.imencode`
					> Ref: https://docs.opencv.org/3.4/d4/da8/group__imgcodecs.html#ga26a67788faa58ade337f8d28ba0eb19e
				> [psi_ij] is the original image size of frame F_ij
				> [gamma] is the compression strength of the image (0 > gamma <= 95)
			Measuring unit:
				Mbits -> bit
			Returns a float value, measured in [bit]
		:return: float
		"""

		# convert Mbits to bit
		tetha_ij_bit = tetha_ij_mbits * pow(10, 6)

		return tetha_ij_bit

	# IMPORTANT!
	def calc_computation_energy(self, tetha_ij_mbits):
		"""
			Description:
				The Total computation energy consumption of drone D_i in time t
			Formula:
				E_i^comp(t) = k * f_i^sigma * T_i^frame(t)

				> [k] is the computational power of drone D_i
					> is a constant that depends on the average switched capacitance and
						the average activity factor
					> The power coefficient [k] may depend also on the CPU frequency
					> Joule/cycle
				> [sigma] is the path loss exponent (2 <= sigma <= 5)
				> [f_i^sigma] is the compression strength of the image (0 > gamma <= 95)
					> cycles/second
			Measuring unit:
				Joule
			Returns a float value, measured in [Joule]
		:return: float
		"""
		# Calculate

		# Calculate [t_i_frame]: Latency to deal with the processing of images in every second
		t_i_frame = algo.calc_t_i_frame(tetha_ij_mbits)
		print(" >> t_i_frame:", t_i_frame)

	def calc_alpha_i_up(self):
		"""
			Description:
				 The uplink rate of the drone D_i to the edge server
			Formula:
				alpha_i^UP(t) = w_i^UL * log2 (1 + ((P_i^Tr * g(i, BS)^(-1*sigma) * abs(h_0)) / N_0))

				> [w_i^UL] is the uplink channel bandwidths between drone D_i and the Base Station
				> [P_i^Tr] is the transmission power of the drone D_i (Joule/Second)
				> [sigma] is the path loss exponent (2 <= sigma <= 5)
				> [g(i, BS)^(-1*sigma)] is the distance between Drone D_i with the Base Station
				> [h_0] is the complex Gaussian channel coefficient based on the complex
						normal distribution CN(0,1) [27]
				> [N_0] is the Additive White Gaussian Noise (AWGN) [28]
			Measuring unit:
				cycles/second (cps)
			Returns a float value, measured in [cycles/second (cps)]
		:return: float
		pass
		"""
		pass

	def calc_g_i_bs(self):
		"""
			Description:
				 The distance between Drone D_i with the Base Station
			Formula:
				g(i, BS) = [(X_BS -X_i)^2 + (Y_BS -Y_i)^2 + (Z_BS -Z_i)^2]
					> where g(i,BS) > r
					> r is the maximum communication radius of Drone D_i to the Base Station.

			Measuring unit:
				Constant
			Returns a float value, measured in a Constant value
		:return: float
		pass
		"""
		pass

	# IMPORTANT!
	def calc_communication_energy(self):
		"""
			Description:
				 The total communication energy consumption of drone D_i in time t
			Formula:
				E_i^comm(t) = P_i^Rx * ((rho * beta_i(t) * tetha_ij(t) * myu_i(t)) / alpha_i^UP(t))

			Measuring unit:
				Joule
			Returns a float value, measured in [Joule]
		:return: float
		"""
		pass

	# IMPORTANT
	def calc_energy_consumption(self):
		"""
			Description:
				 The total energy consumption of drone D_i in time t
			Formula:
				E_i(t) = E_i^comp(t) + E_i^comm(t)

			Measuring unit:
				Joule
			Returns a float value, measured in [Joule]
		:return: float
		"""
		pass
