#!/bin/python

# vim:ts=2:sw=2:noet
from random import randrange, uniform
import numpy as np

def generate_pls(
	eps_mice: float=0.5,
	eps_elep: float=3.0,
	eps_corr: float=5.0,
	n_mice: int=80,
	n_elep: int=20,
	n_corr: int=5 ,
	n_prvblck: int=5,
):
	pls = []
	total_n_pls = n_mice + n_elep + n_corr

	for i in range(total_n_pls):
		remain_pls = total_n_pls - i
		rnd = randrange(0, remain_pls)
		eps_total = 0

		if i == 0:
			eps_total = eps_corr
			n_corr -= 1
		else:
			if rnd < n_mice:
				eps_total = eps_mice
				n_mice -= 1
			elif rnd < n_mice + n_elep:
				eps_total = eps_elep
				n_elep -= 1
			else:
				eps_total = eps_corr
				n_corr -= 1

		step = eps_total / 100
		pl = []
		for _ in range(n_prvblck-1):
			values = np.arange(eps_total-step*25, eps_total+step*25, step=step)
			if values.size == 0:
				demand = 0
			else:
				demand = np.random.choice(values)
			# eps_total -= demand
			pl.append(demand)
		pl.append(eps_total)

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
):
	pls = generate_pls(
		eps_mice,	eps_elep,	eps_corr,
		n_mice,		n_elep, 	n_corr,
		n_prvblck,
	)
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
print(n_mice+n_elep+n_corr)
print_pls(eps_mice, eps_elep, eps_corr, n_mice, n_elep, n_corr, n_prvblck)
