#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import os
import multiprocessing

def onerun(sigma, N, M, K, step, time):
	print("sigma", sigma, "N", N, "M", M, "K", K, "step", step, "time", time)
	foldername = f'sigma_{sigma}_N_{N}_M_{M}_K_{K}_step_{step}'
	csvfile = open(f'./EVALUATION/DATA.SINGLE.PARAM/{foldername}/{time}.csv')
	rainput = f'{N * step}\n{N}\n{M}\n{K}\n'
	for _ in range(N):
		rainput += csvfile.readline()
	csvfile.close()
	os.system(f'echo "{rainput}" | ./oflattack.py > ./EVALUATION/DATA.SINGLE.PARAM/{foldername}/{time}.randomattack.csv')

def multirun(sigma, N, M, K, step, time):
	for i in range(multitimes):
		onerun(sigma, N, M, K, step, time * multitimes + i)

def run_single_param():
	sigma_list = [1.0] # Exponential distribution lambda
	N_list = [50, 100, 150, 200, 250]
	M_list = [5, 10, 15, 20, 25, 30]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	step_list = [1.0]
	times = 100

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
	pool.starmap(multirun, args)
	pool.close()
	pool.join()

if __name__ == '__main__':
	multitimes = 10
	run_single_param()
