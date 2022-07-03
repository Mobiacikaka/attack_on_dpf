#!/bin/python
# vim:ts=2:sw=2:noet
from random import randrange
import numpy as np

def generate_normal_pls( eps_mice: float, eps_elep: float, n_mice: int, n_elep: int, n_prvblck: int):
	pls = []
	total_n_pls = n_mice + n_elep

	for i in range(total_n_pls):
		remain_pls = total_n_pls - i
		rnd = randrange(0, remain_pls)
		eps_total = 0

		if rnd < n_mice:
			eps_total = eps_mice
			n_mice -= 1
		else:
			eps_total = eps_elep
			n_elep -= 1

		step = eps_total / 100
		pl = []
		for _ in range(n_prvblck):
			values = np.arange(eps_total-step*25, eps_total+step*25, step=step)
			if values.size == 0:
				demand = 0
			else:
				demand = np.random.choice(values)
			pl.append(demand)
		pls.append(pl)

	return pls

def print_pls(
	eps_mice: float=0.1,
	eps_elep: float=1.0,
	eps_corr: float=5.0,
	n_mice: int=75,
	n_elep: int=25,
	n_corr: int=5 ,
	n_prvblck: int=5,
) -> None:
	pls = generate_normal_pls(eps_mice,	eps_elep,	n_mice,	n_elep,	n_prvblck)
	for item in pls:
		for item2 in item:
			print('%.4f'%item2, end=" ")
		print()

eps_Global= float(input())
eps_mice	= float(input())
eps_elep	= float(input())
eps_corr	= float(input())
n_mice		= int(input())
n_elep		= int(input())
n_corr		= int(input())
n_prvblck	= int(input())
first_N		= int(input())

eps_mice	*= eps_Global / first_N
eps_elep	*= eps_Global / first_N
eps_corr	*= eps_Global / first_N

print(eps_Global)
print(first_N)
print(n_prvblck)
print(n_mice+n_elep)
print_pls(eps_mice, eps_elep, eps_corr, n_mice, n_elep, n_corr, n_prvblck)
