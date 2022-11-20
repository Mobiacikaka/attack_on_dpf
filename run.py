#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import multiprocessing
import os

def onerun(sigma, N, M, K, step, time):
	print("sigma", sigma, "N", N, "M", M, "K", K, "step", step, "time", time)
	foldername = f'{parent_dir}sigma_{sigma}_N_{N}_M_{M}_K_{K}_step_{step}'
	os.system(f'mkdir -p EVALUATION/{foldername}/')
	param = f'{sigma}\n{N}\n{M}\n{K}\n{step}\n'
	os.system(f'echo "{param}" | ./oflattack.py > "EVALUATION/{foldername}/{time}.csv"')

def multirun(sigma, N, M, K, step, time):
	for i in range(multitimes):
		onerun(sigma, N, M, K, step, time * multitimes + i)

def run_fixed_epsG():
	sigma_list = [0.5, 1.0, 2.0] # Exponential distribution lambda
	M_list = [10]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	times = 100

	eps_G = 120
	N_list = [240, 160, 120, 60, 40]
	#step =  [0.5, 0.75, 1,  2,  3]
	global parent_dir
	parent_dir = 'DATA.FIXED_EPSG/'

	args = [
		(sigma, N, M, int(Kperc * N), eps_G / N, time)
		for sigma in sigma_list
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
		for time in range(times // multitimes)
	]

	pool = multiprocessing.Pool(multiprocessing.cpu_count())
	pool.starmap(multirun, args)
	pool.close()
	pool.join()

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
	parent_dir = ''
	run_fixed_epsG()
