#!/bin/python
# vim:ts=2:sw=2:noet

def generate_normal_pipelines(eps_Global: float=10.0, N: int=20, ratio:float=0.75, N_privateblock:int=1, r_mice:float=0.01, r_elephant:float=0.1) -> list:
	all_pl = []
	n_mice = int(ratio * N)
	n_elephants = N - n_mice
	for _ in range(n_mice):
		pl = []
		for _ in range(N_privateblock):
			pl.append(r_mice * eps_Global)
		all_pl.append(pl)
	for _ in range(n_elephants):
		pl = []
		for _ in range(N_privateblock):
			pl.append(r_elephant * eps_Global)
		all_pl.append(pl)
	return all_pl

def generate_broken_pipelines(eps_Global: float=10.0, N: int=5, r_broken: float=0.3, N_privateblock: int=1) -> list:
	broken_pl = []
	dec = 2
	for _ in range(N*dec):
		pl = []
		for _ in range(N_privateblock):
			pl.append(r_broken * eps_Global / dec)
		broken_pl.append(pl)
	return broken_pl

eps_Global = float(input())
N_normal = int(input())
N_broken = int(input())
ratio_mice_elephant = float(input())
N_privateblock = int(input())
r_mice = float(input())
r_elephant = float(input())
r_broken = float(input())

wp = []
wp += generate_normal_pipelines(eps_Global=eps_Global, N=N_normal, ratio=ratio_mice_elephant, N_privateblock=N_privateblock, r_mice=r_mice, r_elephant=r_elephant)
wp += generate_broken_pipelines(eps_Global=eps_Global, N=N_broken, r_broken=r_broken, N_privateblock=N_privateblock)

print(eps_Global)
print(N_privateblock)
print(len(wp))
for i in range(len(wp)):
	for j in range(N_privateblock):
		print(wp[i][j])
