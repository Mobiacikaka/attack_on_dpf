#!/bin/python
# vim:ts=2:sw=2:noet

from threading import Thread
import numpy as np
import os

def onerun(sigma, N, M, K, step, time):
	foldername = f'sigma_{sigma}_N_{N}_M_{M}_K_{K}_step_{step}'
	os.system(f'mkdir -p EVALUATION/{foldername}/')
	param = f'{sigma}\n{N}\n{M}\n{K}\n{step}\n'
	os.system(f'echo "{param}" | ./oflattack.py > "EVALUATION/{foldername}/{time}.csv"')

def run():
	sigma_list = [1.0] # Exponential distribution lambda
	N_list = list(range(50, 250, 50)) # N benign pipelines
	M_list = list(range(5, 35, 5)) # M blocks
	Kperc_list = list(np.arange(0.1, 0.6, step=0.1)) # K/N percentage
	step_list = [1.0]
	times = 100

	N_list = [100]

	threads = []
	for sigma in sigma_list:
		for N in N_list:
			for M in M_list:
				for Kperc in Kperc_list:
					K = int(Kperc * N)
					for step in step_list:
						for time in range(times):
							print("sigma", sigma, "N", N, "M", M, "K", K, "step", step, "time", time)
							t = Thread(target=onerun, args=(sigma, N, M, K, step, time))
							threads.append(t)
							t.start()
							if len(threads) >= 10:
								for t in threads:
									t.join()
								threads = []

if __name__ == '__main__':
	run()
