#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import multiprocessing, subprocess

multitimes = 10
parent_dir = 'DATA.SINGLE.PARAM/'

def cut(output, foldername, time, N):
	data_original = output[:N]
	file_original = open(f'EVALUATION/{foldername}/{time}.original.txt', 'w')
	file_original.writelines(data_original)
	file_original.close()
	output = output[N:]
	while len(output) != 0:
		data_func = output[:N+3]
		file_func = open(f'EVALUATION/{foldername}/{time}.{data_func[0]}.txt', 'w')
		file_func.writelines(data_func)
		output = output[N+3:]
		file_func.close()

def onerun(N, M, K, step, time):
	print("N", N, "M", M, "K", K, "step", step, "time", time)
	foldername = f'{parent_dir}N_{N}_M_{M}_K_{K}_step_{step}'
	param = f'{N}\n{M}\n{K}\n{step}\n'

	subprocess.run(['mkdir', '-p', f'EVALUATION/{foldername}/'])
	output = subprocess.Popen(
		['python', 'oflattack.py'], 
		stdin=subprocess.PIPE,
		stdout=subprocess.PIPE,
		stderr=subprocess.STDOUT,
	)
	output = output.communicate(input=param.encode())[0]
	output = output.decode('utf-8')
	output = output.split('\n')[:-1]
	cut(output, foldername, time, N)

def multirun(N, M, K, step, time):
	for i in range(multitimes):
		onerun(N, M, K, step, time * multitimes + i)

def run_fixed_epsG():
	M_list = [10]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	times = 100

	eps_G = 120
	N_list = [240, 160, 120, 60, 40]
	#step =  [0.5, 0.75, 1,  2,  3]
	global parent_dir
	parent_dir = 'DATA.FIXED_EPSG/'

	args = [
		(N, M, int(Kperc * N), eps_G / N, time)
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
	N_list = [50, 100, 150, 200, 250]
	M_list = [5, 10, 15, 20, 25, 30]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	step_list = [1.0]
	times = 100

	args = [
		(N, M, int(Kperc * N), step, time)
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
	run_single_param()
