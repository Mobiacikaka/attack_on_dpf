#!/usr/bin/python3
# vim:ts=2:sw=2:noet

import os

dirs = os.listdir('./EVALUATION/DATA.SINGLE.PARAM')

if 'images' in dirs:
	dirs.remove('images')

sigma = 1.0
N = 0
M = 0
K = 0
step = 1.0

for dirname in dirs:
	dirsplit = dirname.split('_')
	for i in range(len(dirsplit)):
		if dirsplit[i] == 'sigma':
			sigma = float(dirsplit[i+1])
		elif dirsplit[i] == 'N':
			N = int(dirsplit[i+1])
		elif dirsplit[i] == 'M':
			M = int(dirsplit[i+1])
		elif dirsplit[i] == 'K':
			K = int(dirsplit[i+1])
		elif dirsplit[i] == 'step':
			step = float(dirsplit[i+1])
	for i in range(100):
		csvfile = open(f'./EVALUATION/DATA.SINGLE.PARAM/{dirname}/{i}.csv')
		# random attack input
		rainput = f'{N * step}\n{N}\n{M}\n{K}\n'
		for j in range(N):
			rainput += csvfile.readline()
		print('N', N, 'M', M, 'K', K, 'step', step, 'time', i)
		os.system(f'echo "{rainput}" | ./oflattack.py > ./EVALUATION/DATA.SINGLE.PARAM/{dirname}/{i}.RandomAttack.csv')
