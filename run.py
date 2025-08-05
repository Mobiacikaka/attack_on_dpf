#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import multiprocessing, subprocess

multitimes = 1
parent_dir = 'test/'

def cut(output, foldername, time, config, read_flag):
	N = config['N']
	K = config['K']
	data_original = output[:N]
	delta = 4
	if not read_flag:
		if len(data_original) < N:
			print(f'Error occur in {foldername} time {time}')
			errorfile = open(f'EVALUATION/{foldername}/{time}.error.txt', 'w')
			for line in output:
				errorfile.write(line + '\n')
			return
		file_original = open(f'EVALUATION/{foldername}/{time}.original.txt', 'w')
		for line in data_original:
			file_original.write(line+'\n')
		file_original.close()
		output = output[N:]
	while len(output) != 0:
		if len(output) < K + delta:
			print(f'Error occur in {foldername} time {time}')
			errorfile = open(f'EVALUATION/{foldername}/{time}.error.txt', 'w')
			for line in output:
				errorfile.write(line + '\n')
			return
		data_func = output[:K + delta]
		file_func = open(f'EVALUATION/{foldername}/{time}.{data_func[0]}.txt', 'w')
		for line in data_func:
			file_func.write(line+'\n')
		output = output[K + delta:]
		file_func.close()

def readoriginal(foldername, time) -> str:
	_file = open(f'EVALUATION/{foldername}/{time}.original.txt')
	lines = _file.readlines()
	oridataset = ''
	for line in lines:
		oridataset += line
	return oridataset

def onerun(config: dict, time, read_flag):
	foldername = ''
	param = ''
	for name, val in config.items():
		print(f'{name}\t{val}\t', end='')
		foldername += f'{name}_{val}_'
		param += f'{val}\n'
	# cutpoint = foldername.find('_ratio_')
	# foldername = foldername[:cutpoint]
	print(f'time\t{time}')
	foldername = parent_dir + foldername

	param += f'{read_flag}\n'
	if read_flag:
		oridataset = readoriginal(foldername, time)
		param += oridataset

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
	cut(output, foldername, time, config, read_flag)

def multirun(config, time, read_flag):
	for i in range(multitimes):
		onerun(config, time * multitimes + i, read_flag)

def run_fixed_epsG():
	M_list = [10]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	times = 100

	eps_G = 120
	N_list = [240, 160, 120, 60, 40]
	#step =  [0.5, 0.75, 1,  2,  3]
	ratio_list = [0, 0.75]
	exp_elephant_list = [1.0, 2.0, 3.0, 4.0]

	global parent_dir
	parent_dir = 'DATA.FIXED.EPS_G/'

	args = [
		({
			'N': N,
			'M': M,
			'K': int(Kperc * N),
			'step': float(eps_G / N),
			'ratio': ratio,
			'exp_mice': exp_elephant/10,
			'exp_elephant': exp_elephant,
		}, time, True)
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
		for time in range(times // multitimes)
		for ratio in ratio_list
		for exp_elephant in exp_elephant_list
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
	read_flag = True

	args = [
		({
			'N': N,
			'M': M,
			'K': int(Kperc * N),
			'step': step,
			'ratio': 0,
			'exp_mice': 0.1,
			'exp_elephant': 1.0,
		}, time, read_flag)
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
	run_fixed_epsG()
	# run_single_param()
