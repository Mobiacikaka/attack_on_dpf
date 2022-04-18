#!/bin/python
# vim:ts=2:sw=2:noet
import numpy as np

def generate_poison_pls(eps_corr: float, n_corr: int, n_prvblck: int) -> list:
	pls = []
	for _ in range(n_corr):
		pl = []
		for _ in range(n_prvblck):
			values = np.array([eps_corr])
			if values.size == 0:
				demand = 0
			else:
				demand = np.random.choice(values)
			pl.append(demand)
		pls.append(pl)
	return pls

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

print(n_corr)
poison_pls = generate_poison_pls(eps_corr, n_corr, n_prvblck)
for pl in poison_pls:
	for demand in pl:
		print('%.4f'%demand, end=" ")
	print()
