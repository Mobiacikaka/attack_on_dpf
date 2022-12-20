#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import statistics
from matplotlib import subprocess
import numpy as np
import matplotlib.pyplot as plt
import os

def read_onetime(foldername, times) -> list:
	res = []
	for funcname in funcname_list:
		file = open(f'{foldername}/{times}.{funcname}.txt')
		lines = file.readlines()
		res.append(float(lines[1].replace('\n', '')))
	return res

def read_folder(foldername):
	res_hundredtimes = []
	for _ in range(len(funcname_list)):
		res_hundredtimes.append([])
	print(foldername)
	for times in range(100):
		res_onetime = read_onetime(foldername, times)
		for i in range(len(funcname_list)):
			try:
				res_hundredtimes[i].append(res_onetime[i])
			except:
				print("error", foldername, times)
				exit(0)
	return res_hundredtimes

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

def draw_N_effect(
	res_dict,
	parent_folder,
	N_list = [50, 100, 150, 200, 250],
	M_list = [5, 10, 15, 20, 25, 30],
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5],
	step_list = [1.0],
):
	foldername = parent_folder + 'images'
	subprocess.run(['mkdir', '-p', foldername])

	args = [
		(M, Kperc, step)
		for M in M_list
		for Kperc in Kperc_list
		for step in step_list
	]

	for arg in args:
		M, Kperc, step = arg
		res = []
		mean = [[0 for _ in range(len(N_list))] for _ in range(len(funcname_list))]
		stdev = [[0 for _ in range(len(N_list))] for _ in range(len(funcname_list))]
		for i in range(len(N_list)):
			N = N_list[i]
			res = res_dict[(N, M, int(Kperc * N), step)]
			for j in range(len(res)):
				mean_func, stdev_func = res[j]
				mean[j][i] = mean_func
				stdev[j][i] = stdev_func
		for i in range(len(funcname_list)):
			plt.errorbar(N_list, mean[i], stdev[i], label=funcname_list[i], marker=markers[i])
		plt.xlabel('N')
		plt.ylabel('Gain Fraction')
		plt.xticks(N_list)
		plt.yticks(yticks)
		plt.legend(fontsize='medium')
		figurename = f'{foldername}/N_M_{M}_Kperc_{Kperc}_step_{step}.eps'
		plt.tight_layout()
		plt.grid()
		plt.savefig(figurename, format='eps')
		plt.clf()

def draw_N_effect2(
	res_dicts: list,
	N_list = [50, 100, 150, 200, 250],
	M_list = [10],
	Kperc_list = [0.3],
	step_list = [1.0],
):
	foldername = 'images'
	subprocess.run(['mkdir', '-p', foldername])

	args = [
		(M, Kperc, step)
		for M in M_list
		for Kperc in Kperc_list
		for step in step_list
	]

	for arg in args:
		M, Kperc, step = arg
		mean = [[[0 for _ in range(len(N_list))] for _ in range(len(funcname_list))] for _ in range(2)]
		stdev = [[[0 for _ in range(len(N_list))] for _ in range(len(funcname_list))] for _ in range(2)]
		for i in range(len(N_list)):
			N = N_list[i]
			res = [[], []]
			res[0] = res_dicts[0][(N, M, int(Kperc * N), step)]
			res[1] = res_dicts[1][(N, M, int(Kperc * N), step)]
			for k in range(2):
				for j in range(len(res[0])):
					mean_func, stdev_func = res[k][j]
					mean[k][j][i] = mean_func
					stdev[k][j][i] = stdev_func
		fig, axs = plt.subplots(1, 2, sharex=True, sharey=True)
		for k in range(2):
			for i in range(len(funcname_list)):
				axs[k].errorbar(N_list, mean[k][i], stdev[k][i], label=funcname_list[i], marker=markers[i])
		for ax in axs:
			ax.set(xlabel='N', ylabel='Gain Fraction', xticks=N_list, yticks=yticks, title='yes')
			pos = ax.get_position()
			ax.set_position([pos.x0, pos.y0, pos.width, pos.height * 0.85])
			ax.grid()
		fig.legend(funcname_list, ncol=3, loc="upper center")
		# plt.rc('font', size=10)          # controls default text sizes
		# plt.rc('axes', titlesize=8)     # fontsize of the axes title
		# plt.rc('axes', labelsize=8)     # fontsize of the x and y labels
		# plt.rc('xtick', labelsize=8)    # fontsize of the tick labels
		# plt.rc('ytick', labelsize=8)    # fontsize of the tick labels
		# plt.rc('legend', fontsize=10)    # legend fontsize
		# plt.rc('figure', titlesize=10)   # fontsize of the figure title
		plt.tight_layout()
		plt.show()

def draw_M_effect(
	res_dict,
	parent_folder,
	N_list = [50, 100, 150, 200, 250],
	M_list = [5, 10, 15, 20, 25, 30],
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5],
	step_list = [1.0],
):
	foldername = parent_folder + 'images'
	subprocess.run(['mkdir', '-p', foldername])

	args = [
		(N, Kperc, step)
		for N in N_list
		for Kperc in Kperc_list
		for step in step_list
	]

	for arg in args:
		N, Kperc, step = arg
		res = []
		mean = [[0 for _ in range(len(M_list))] for _ in range(len(funcname_list))]
		stdev = [[0 for _ in range(len(M_list))] for _ in range(len(funcname_list))]
		for i in range(len(M_list)):
			M = M_list[i]
			res = res_dict[(N, M, int(Kperc * N), step)]
			for j in range(len(res)):
				mean_func, stdev_func = res[j]
				mean[j][i] = mean_func
				stdev[j][i] = stdev_func
		for i in range(len(funcname_list)):
			plt.errorbar(M_list, mean[i], stdev[i], label=funcname_list[i], marker=markers[i])
		plt.xlabel('M')
		plt.ylabel('Gain Fraction')
		plt.xticks(M_list)
		plt.yticks(yticks)
		plt.legend(fontsize='medium')
		figurename = f'{foldername}/M_N_{N}_Kperc_{Kperc}_step_{step}.eps'
		plt.tight_layout()
		plt.grid()
		plt.savefig(figurename, format='eps')
		plt.clf()

def draw_K_effect(
	res_dict,
	parent_folder,
	N_list = [50, 100, 150, 200, 250],
	M_list = [5, 10, 15, 20, 25, 30],
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5],
	step_list = [1.0],
):
	foldername = parent_folder + 'images'
	subprocess.run(['mkdir', '-p', foldername])

	args = [
		(N, M, step)
		for N in N_list
		for M in M_list
		for step in step_list
	]

	for arg in args:
		N, M, step = arg
		res = []
		mean = [[0 for _ in range(len(Kperc_list))] for _ in range(len(funcname_list))]
		stdev = [[0 for _ in range(len(Kperc_list))] for _ in range(len(funcname_list))]
		for i in range(len(Kperc_list)):
			Kperc = Kperc_list[i]
			res = res_dict[(N, M, int(Kperc * N), step)]
			for j in range(len(res)):
				mean_func, stdev_func = res[j]
				mean[j][i] = mean_func
				stdev[j][i] = stdev_func
		for i in range(len(funcname_list)):
			plt.errorbar(Kperc_list, mean[i], stdev[i], label=funcname_list[i], marker=markers[i])
		plt.xlabel('K/N')
		plt.ylabel('Gain Fraction')
		plt.xticks(Kperc_list)
		plt.yticks(yticks)
		plt.legend(fontsize='medium')
		figurename = f'{foldername}/Kperc_N_{N}_M_{M}_step_{step}.eps'
		plt.tight_layout()
		plt.grid()
		plt.savefig(figurename, format='eps')
		plt.clf()

def Draw1(draw_N_flag=True, draw_M_flag=True, draw_K_flag=True):
	parent_folder = './EVALUATION/DATA.MICE.AND.ELEPHANT.1/'
	N_list = [50, 100, 150, 200, 250]
	M_list = [5, 10, 15, 20, 25, 30]
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]

	args = [
		(N, M, int(Kperc * N), 1.0)
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
	]

	res_dict = {}
	for arg in args:
		N, M, K, step = arg
		foldername = parent_folder + f'N_{N}_M_{M}_K_{K}_step_{step}'
		res_hundredtimes = read_folder(foldername)
		y = [] # [(mean1, stdev1), (mean2, stdev2), (mean3, stdev3)]
		for i in range(len(funcname_list)):
			mean = statistics.mean(res_hundredtimes[i])
			stdev = statistics.stdev(res_hundredtimes[i])
			# print(mean, stdev, funcname_list[i])
			y.append((mean, stdev))
		res_dict[arg] = y

	if draw_N_flag:
		draw_N_effect(res_dict, parent_folder, N_list=N_list, M_list=M_list, Kperc_list=Kperc_list)

	if draw_M_flag:
		draw_M_effect(res_dict, parent_folder, N_list=N_list, M_list=M_list, Kperc_list=Kperc_list)

	if draw_K_flag:
		draw_K_effect(res_dict, parent_folder, N_list=N_list, M_list=M_list, Kperc_list=Kperc_list)

def Draw2(draw_N_flag=True, draw_M_flag=True, draw_K_flag=True):
	parent_folder1 = './EVALUATION/DATA.MICE.AND.ELEPHANT.1/'
	parent_folder2 = './EVALUATION/DATA.MICE.AND.ELEPHANT.2/'

	N_list = [50, 100, 150, 200, 250]
	M_list = [10]
	Kperc_list = [0.3]

	args = [
		(N, M, int(Kperc * N), 1.0)
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
	]

	res_dict1 = {}
	res_dict2 = {}
	def read_big_folder(parent_folder):
		res_dict = {}
		for arg in args:
			N, M, K, step = arg
			foldername = parent_folder + f'N_{N}_M_{M}_K_{K}_step_{step}'
			res_hundredtimes = read_folder(foldername)
			y = [] # [(mean1, stdev1), (mean2, stdev2), (mean3, stdev3)]
			for i in range(len(funcname_list)):
				mean = statistics.mean(res_hundredtimes[i])
				stdev = statistics.stdev(res_hundredtimes[i])
				# print(mean, stdev, funcname_list[i])
				y.append((mean, stdev))
			res_dict[arg] = y
		return res_dict
	res_dict1 = read_big_folder(parent_folder1)
	res_dict2 = read_big_folder(parent_folder2)

	if draw_N_flag:
		draw_N_effect2([res_dict1, res_dict2], N_list)

	if draw_M_flag:
		pass

	if draw_K_flag:
		pass

if __name__ == '__main__':
	funcname_list = [
		'RandomAttack',
		'NaiveGreedy',
		'BlockGreedy',
		'DynamicSequentialAttack_std',
		'DynamicSequentialAttack_mod',
	]
	markers = ['o', 'v', 'P', 's', 'p']
	yticks = np.arange(0, 1.1, 0.1)

	# Draw1(draw_N_flag=True, draw_M_flag=True, draw_K_flag=True)
	Draw2(draw_N_flag=True, draw_M_flag=True, draw_K_flag=True)
