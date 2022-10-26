#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import statistics
import matplotlib.pyplot as plt
import os

def read_onetime(folderargs, times) -> list:
	sigma, N, M, K, step = folderargs
	foldername = f'sigma_{sigma}_N_{N}_M_{M}_K_{K}_step_{step}'
	file = open(f'EVALUATION/{foldername}/{times}.csv')
	lines = file.readlines()
	file.close()
	res = []
	for i in range(len(lines)):
		if lines[i].find('function') == 1:
			res.append(float(lines[i+2]))
	return res

def read_folder(folderargs):
	res_hundredtimes = [[], [], [], []]
	print(folderargs)
	for times in range(100):
		res_onetime = read_onetime(folderargs, times)
		for i in range(4):
			try:
				res_hundredtimes[i].append(res_onetime[i])
			except:
				print("error", folderargs, times)
				exit(0)
	return res_hundredtimes

def draw_K_effect():
	N_list = list(range(50, 250, 50))
	M_list = list(range(5, 35, 5))
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]

	for N in N_list:
		for M in M_list:
			## Draw Picture
			y = [[], [], [], []]
			for Kperc in Kperc_list:
				folderargs = (1.0, N, M, int(Kperc * N), 1.0)
				res_hundredtimes = read_folder(folderargs)
				for i in range(len(res_hundredtimes)):
					y[i].append(statistics.mean(res_hundredtimes[i]))
			print(y)
			for i in range(len(y)):
				plt.plot(Kperc_list, y[i], label=f'function {i}', marker='o')
			plt.title(f'N: {N}, M: {M}')
			plt.xlabel('K/N')
			plt.ylabel('Percentage')
			plt.xticks(Kperc_list)
			plt.legend()
			os.system('mkdir -p EVALUATION/images/K_EFFECT')
			plt.savefig(f'EVALUATION/images/K_EFFECT/N_{N}_M_{M}_sigma_{1.0}_step_{1.0}.svg', format='svg')
			plt.clf()

def draw_M_effect():
	N_list = list(range(50, 250, 50))
	M_list = list(range(5, 35, 5))
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]

	for N in N_list:
		for Kperc in Kperc_list:
			## Draw Picture
			y = [[], [], [], []]
			for M in M_list:
				folderargs = (1.0, N, M, int(Kperc * N), 1.0)
				res_hundredtimes = read_folder(folderargs)
				for i in range(len(res_hundredtimes)):
					y[i].append(statistics.mean(res_hundredtimes[i]))
			print(y)
			for i in range(len(y)):
				plt.plot(M_list, y[i], label=f'function {i}', marker='o')
			plt.title(f'N: {N}, K/N: {Kperc}')
			plt.xlabel('M')
			plt.ylabel('Percentage')
			plt.xticks(M_list)
			plt.legend()
			os.system('mkdir -p EVALUATION/images/M_EFFECT')
			plt.savefig(f'EVALUATION/images/M_EFFECT/N_{N}_Kperc_{Kperc}_sigma_{1.0}_step_{1.0}.svg', format='svg')
			plt.clf()

def draw_N_effect():
	N_list = list(range(50, 250, 50))
	M_list = list(range(5, 35, 5))
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]

	for M in M_list:
		for Kperc in Kperc_list:
			## Draw Picture
			y = [[], [], [], []]
			for N in N_list:
				folderargs = (1.0, N, M, int(Kperc * N), 1.0)
				res_hundredtimes = read_folder(folderargs)
				for i in range(len(res_hundredtimes)):
					y[i].append(statistics.mean(res_hundredtimes[i]))
			print(y)
			for i in range(len(y)):
				plt.plot(N_list, y[i], label=f'function {i}', marker='o')
			plt.title(f'M: {M}, K/N: {Kperc}')
			plt.xlabel('N')
			plt.ylabel('percentage')
			plt.xticks(N_list)
			plt.legend()
			os.system('mkdir -p EVALUATION/images/N_EFFECT')
			plt.savefig(f'EVALUATION/images/N_EFFECT/M_{M}_Kperc_{Kperc}_sigma_{1.0}_step_{1.0}.svg', format='svg')
			plt.clf()

def main():
	sigma_list = [1.0]
	N_list = list(range(200, 250, 50))
	M_list = list(range(5, 35, 5))
	Kperc_list = [0.1, 0.2, 0.3, 0.4, 0.5]
	step_list = [1.0]
	foldernames = [
		(sigma, N, M, int(Kperc * N), step)
		for sigma in sigma_list
		for N in N_list
		for M in M_list
		for Kperc in Kperc_list
		for step in step_list
	]

	for folderargs in foldernames:
		read_folder(folderargs)

draw_K_effect()
# draw_N_effect()
# draw_M_effect()
