#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import statistics
import numpy as np
import matplotlib.pyplot as plt
import os

def read_onetime(folderargs, times, datafolder) -> list:
	sigma, N, M, K, step = folderargs
	foldername = f'sigma_{sigma}_N_{N}_M_{M}_K_{K}_step_{step}'
	file = open(f'EVALUATION/{datafolder}/{foldername}/{times}.csv')
	lines = file.readlines()
	file.close()
	res = []
	for i in range(len(lines)):
		if lines[i].find('function') == 1:
			res.append(float(lines[i+2]))
	return res

def read_folder(folderargs, datafolder, funcnum=5):
	res_hundredtimes = []
	for _ in range(funcnum):
		res_hundredtimes.append([])
	print(folderargs)
	for times in range(100):
		res_onetime = read_onetime(folderargs, times, datafolder)
		for i in range(funcnum):
			try:
				res_hundredtimes[i].append(res_onetime[i])
			except:
				print("error", folderargs, times)
				exit(0)
	return res_hundredtimes

def DrawGraphics(config: dict):
	sigma_list = config.get('sigma_list', [1.0])
	N_list = config.get('N_list', [100])
	M_list = config.get('M_list', [10])
	Kperc_list = config.get('Kperc_list', [0.1])
	step_list = config.get('sigma_list', [1.0])
	datafolder = config.get('datafolder', '')
	funcname = config.get('funcname', ['GTR', 'Block Greedy', 'DSA1', 'DSA2', 'Random Attack'])
	markers = config.get('markers', ['o', 'v', '^', 's', 'p'])
	xlabel = config.get('xlabel', '')
	ylabel = config.get('ylabel', 'Gain Fraction')

	args = [
		(sigma, N, M, int(Kperc * N), step)
		for sigma in sigma_list
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
		for step in step_list
	]

	res_dict = {}
	for folderargs in args:
		y = []
		res_hundredtimes = read_folder(folderargs, datafolder)
		for i in range(len(res_hundredtimes)):
			y.append(statistics.mean(res_hundredtimes[i]))
		res_dict[folderargs] = y

	for item in res_dict.items():
		print(item)

def draw_K_effect():
	N_list = [50, 100, 150, 200]
	M_list = [5, 10, 15, 20, 25, 30]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	step = 1.0
	datafolder = 'DATA.SINGLE.PARAM'

	for N in N_list:
		for M in M_list:
			## Draw Picture
			y = [[], [], [], [], []]
			err = [[], [], [], [], []]
			for Kperc in Kperc_list:
				folderargs = (1.0, N, M, int(Kperc * N), step)
				res_hundredtimes = read_folder(folderargs, datafolder)
				for i in range(len(funcname)):
					y[i].append(statistics.mean(res_hundredtimes[i]))
					err[i].append(statistics.stdev(res_hundredtimes[i]))
			for i in range(len(funcname)):
				plt.errorbar(Kperc_list, y[i], err[i], label=funcname[i], marker=markers[i], capsize=4)
				# plt.plot(Kperc_list, y[i], label=funcname[i], marker=markers[i])
			plt.xlabel('K/N')
			plt.ylabel('Gain Fraction')
			plt.xticks(Kperc_list)
			plt.yticks(yticks)
			plt.legend()
			os.system(f'mkdir -p EVALUATION/{datafolder}/images/')
			figname = f'EVALUATION/{datafolder}/images/K_Effect_N{N}_M{M}.eps'
			plt.tight_layout()
			plt.savefig(figname, format='eps')
			plt.clf()

def draw_M_effect():
	N_list = list(range(50, 250, 50))
	M_list = list(range(5, 35, 5))
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	step = 1.0
	datafolder = 'DATA.SINGLE.PARAM'

	for N in N_list:
		for Kperc in Kperc_list:
			## Draw Picture
			y = [[], [], [], [], []]
			err = [[], [], [], [], []]
			for M in M_list:
				folderargs = (1.0, N, M, int(Kperc * N), step)
				res_hundredtimes = read_folder(folderargs, datafolder)
				for i in range(len(funcname)):
					y[i].append(statistics.mean(res_hundredtimes[i]))
					err[i].append(statistics.stdev(res_hundredtimes[i]))
			for i in range(len(funcname)):
				plt.errorbar(M_list, y[i], err[i], label=funcname[i], marker=markers[i], capsize=4)
				# plt.plot(M_list, y[i], label=funcname[i], marker=markers[i])
			plt.xlabel('M')
			plt.ylabel('Gain Fraction')
			plt.xticks(M_list)
			plt.yticks(yticks)
			plt.legend()
			os.system(f'mkdir -p EVALUATION/{datafolder}/images/')
			figname = f'EVALUATION/{datafolder}/images/M_Effect_N{N}_Kperc{Kperc}.eps'
			plt.tight_layout()
			plt.savefig(figname, format='eps')
			plt.clf()

def draw_N_effect():
	N_list = [50, 100, 150, 200]
	M_list = [5, 10, 15, 20, 25, 30]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	step = 1.0
	datafolder = 'DATA.SINGLE.PARAM'

	for M in M_list:
		for Kperc in Kperc_list:
			## Draw Picture
			y = [[], [], [], [], []]
			err = [[], [], [], [], []]
			for N in N_list:
				folderargs = (1.0, N, M, int(Kperc * N), step)
				res_hundredtimes = read_folder(folderargs, datafolder)
				for i in range(len(funcname)):
					y[i].append(statistics.mean(res_hundredtimes[i]))
					err[i].append(statistics.stdev(res_hundredtimes[i]))
			for i in range(len(funcname)):
				plt.errorbar(N_list, y[i], err[i], label=funcname[i], marker=markers[i], capsize=4)
				# plt.plot(N_list, y[i], label=funcname[i], marker=markers[i])
			plt.xlabel('N')
			plt.ylabel('Gain Fraction')
			plt.xticks(N_list)
			plt.yticks(yticks)
			plt.legend()
			os.system(f'mkdir -p EVALUATION/{datafolder}/images/')
			figname = f'EVALUATION/{datafolder}/images/N_Effect_M{M}_Kperc{Kperc}.eps'
			plt.tight_layout()
			plt.savefig(figname, format='eps')
			plt.clf()

def draw_GRAIN_effect():
	N_list = [40, 60, 120, 160, 240]
	M_list = [10]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	datafolder = 'DATA.FIXED.EPS_G'
	funcname = ['GTR', 'Block Greedy', 'DSA1', 'DSA2']
	eps_G = 120.0
	funcnum = 4

	for sigma in [0.5, 1.0, 2.0]:
		for M in M_list:
			for Kperc in Kperc_list:
				## Draw Picture
				y = [[], [], [], [], []]
				for N in N_list:
					folderargs = (sigma, N, M, int(Kperc * N), eps_G/N)
					res_hundredtimes = read_folder(folderargs, datafolder, funcnum)
					for i in range(funcnum):
						y[i].append(statistics.mean(res_hundredtimes[i]) / (eps_G/N))
				for i in range(funcnum):
					plt.plot(N_list, y[i], label=funcname[i], marker='o')
				plt.xlabel('N')
				plt.ylabel('Gain Fraction')
				plt.xticks(N_list)
				plt.legend()
				os.system(f'mkdir -p EVALUATION/{datafolder}/images/')
				filename = f'EVALUATION/{datafolder}/images/Grain_Effect_sigma{sigma}_epsG{eps_G}_M{M}_Kperc{Kperc}.eps'
				plt.tight_layout()
				plt.savefig(filename, format='eps')
				plt.clf()

def main():
	config = {
		'N_list': [50, 100, 150, 200],
		'M_list': [5, 10, 15, 20, 25, 30],
		'Kperc_list': [0.1, 0.2, 0.3, 0.4, 0.5],
		'datafolder': 'DATA.SINGLE.PARAM',
	}
	DrawGraphics(config)

def Draw1():
	parent_folder = 'DATA.MICE.AND.ELEPHANT.1'

if __name__ == '__main__':
	plt.rc('font', size=10)          # controls default text sizes
	plt.rc('axes', titlesize=10)     # fontsize of the axes title
	plt.rc('axes', labelsize=18)     # fontsize of the x and y labels
	plt.rc('xtick', labelsize=18)    # fontsize of the tick labels
	plt.rc('ytick', labelsize=18)    # fontsize of the tick labels
	plt.rc('legend', fontsize=10)    # legend fontsize
	plt.rc('figure', titlesize=18)   # fontsize of the figure title

	funcname = ['GTR', 'Block Greedy', 'DSA1', 'DSA2', 'RandomAttack']
	markers = ['o', 'v', 'P', 's', 'p']
	yticks = np.arange(0.2, 1.1, 0.1)

	# draw_K_effect()
	# draw_M_effect()
	# draw_N_effect()
	draw_GRAIN_effect()
	# main()
