from ddp_lib.dataset import Dataset
from ddp_lib.algorithm import Algorithm
import dis

# DATASET_FILEPATH = "./dataset/bandwidth_usage_Q=32.csv"
DATASET_FILEPATH = "./dataset/bandwidth_usage_Q=32_no_header.csv"

# define constant variables
DEFAULT_MYU = 10  # FPS; default is 10
RHO = 1  # an offloading coefficient (0 >= ρ >= 1)
GAMMA = 32  # FYI: dataset `bandwidth_usage_Q=32_no_header.csv` use `32` compression quality
SIGMA = 3  # (2 <= SIGMA <= 5); According to [22] SIGMA can be set as 3 (usually close to 3)

# Ref 1: http://www.kylesconverter.com/frequency/gigahertz-to-cycles-per-second
# Ref 2: https://developer.nvidia.com/embedded/jetson-nano-developer-kit
F_I = 1430000000  # 1.43 GHz -> 1430000000 cps (cycles/second)

# Simplified value
H_0 = 1

# Ref: https://www.rapidtables.com/convert/power/dBm_to_Watt.html
N_0 = 10000000  # 100 dBm -> 10000000 Watt

# load dataaset
dataset_obj = Dataset(DATASET_FILEPATH)
dataset_obj.load_dataset()
dataset = dataset_obj.get_dataset()

# print(dataset)

# setu[ algorithm
algo = Algorithm(
	defaulf_myu=DEFAULT_MYU,
	rho=RHO,
	gamma=GAMMA,
	sigma=SIGMA,
	f_i=F_I,
	h_0=H_0,
	N_0=N_0,
)

"""
	Goal: Get Energy cosumption in each frame (each loop)
	
	Flow:
	1. Loop each dataset
	2. Calculate Energy Consumption and store the value
"""

for data in dataset:

	tetha_ij_mbits = data[dataset_obj.ENCODED_IMG_SIZE_MBITS]


	computation_energy = algo.calc_computation_energy(tetha_ij_mbits)

# sample to get the function name
# print(algo.calc_beta_i.__name__)
