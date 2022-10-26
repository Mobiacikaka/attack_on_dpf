#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import multiprocessing
import numpy as np
import os

def onerun(sigma, N, M, K, step, time):
	print("sigma", sigma, "N", N, "M", M, "K", K, "step", step, "time", time)
	foldername = f'sigma_{sigma}_N_{N}_M_{M}_K_{K}_step_{step}'
	os.system(f'mkdir -p EVALUATION/{foldername}/')
	param = f'{sigma}\n{N}\n{M}\n{K}\n{step}\n'
	os.system(f'echo "{param}" | ./oflattack.py > "EVALUATION/{foldername}/{time}.csv"')

def multirun(sigma, N, M, K, step, time):
	for i in range(multitimes):
		onerun(sigma, N, M, K, step, time * multitimes + i)

def run():
	sigma_list = [1.0] # Exponential distribution lambda
	N_list = list(range(50, 250, 50)) # N benign pipelines
	M_list = list(range(5, 35, 5)) # M blocks
	Kperc_list = list(np.arange(0.1, 0.6, step=0.1)) # K/N percentage
	step_list = [1.0]
	times = 100

	N_list = [50]
	M_list = [25, 30]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]

	args = [
		(sigma, N, M, int(Kperc * N), step, time)
		for sigma in sigma_list
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
		for step in step_list
		for time in range(times // multitimes)
	]

	pool = multiprocessing.Pool(multiprocessing.cpu_count())
	pool.starmap(onerun, args)
	pool.close()
	pool.join()

if __name__ == '__main__':
	multitimes = 10
	run()
