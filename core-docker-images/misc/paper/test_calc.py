from math import log2

coba = (0.0093 * pow(10, 24)) * (0.301 * pow(10, 0)) * \
	   (1 + (
		   1.258/pow(10, -15)
	   ))

print(coba)  # 3.521519400000002e+36 = 3.52 x 10^36
print(pow(10, 0))
print(pow(10, -15))

val = 1 * (1.258 / pow(10, -15))
calc = log2(val)
calc = round(calc, 2)
print(">>> val:", val)
print(">>> calc:", calc)

# paper: https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=7914660
cpu_freq = 400 * pow(10, 6)  # cycle/s
comp_power = 0.8  # Watt
k = comp_power / pow(cpu_freq, 3)
print(" >>> k=", k)
print(" >>> pow(10, 6)=", pow(10, 6))

ghz = 1.4 * pow(10, 9)
print(" >>> ghz=", ghz)

freq = 1.4
comp = (k * pow(freq, 3) * 46) / freq
print(" >>> comp=", comp)
#####################


