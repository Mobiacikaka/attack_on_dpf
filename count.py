#!/bin/python3
# vim:ts=2:sw=2:noet
from random import uniform
import numpy as np

def count(datablock: list) -> int:
	return sum(datablock)

def count_with_dp(datablock: list, mu: float=0, b: float=1) -> float:
	c = count(datablock) + np.random.laplace(loc=mu, scale=b)
	return c

def random_draw_datablocks(N: int=5, n: int=100) -> list:
	datablocks = []
	for _ in range(N):
		_0_ratio = uniform(0.25, 0.75)
		datablock = np.random.choice(a=np.array([0, 1]), p=[_0_ratio, 1-_0_ratio], size=n)
		datablocks.append(datablock)

	return datablocks

def run(eps_total: float=1.0, eps_step: float=0.1):
	datablocks = random_draw_datablocks(n=1000)
	sens = 1
	
	sum_total_list = [count_with_dp(datablock, b=sens/eps_total) for datablock in datablocks]
	sum_total = sum(sum_total_list)
	print(sum_total)

	times = int(eps_total // eps_step)
	sum_divide_list = []
	for _ in range(times):
		sum_divide_list.append([count_with_dp(datablock, b=sens/eps_step) for datablock in datablocks])

	sum_divide = sum([sum(i) for i in sum_divide_list]) / times
	print(sum_divide)
	print( abs(sum_divide - sum_total) )
	print()

eps_Global = float(input())
first_NPL = int(input())
NPB = int(input())
NPL = int(input())
pls = []
for i in range(NPL):
	pl = []
	line = input()
	pl = [float(item) for item in line.split(" ") if len(item) > 0]
	pls.append(pl)

poison_pls_no = str(input()).split(" ")
poison_pls_no.pop(len(poison_pls_no) - 1)
poison_pls_no = [int(i) for i in poison_pls_no]

unsorted_pl_no = str(input()).split(" ")
unsorted_pl_no.pop(len(unsorted_pl_no) - 1)
unsorted_pl_no = [int(i) for i in unsorted_pl_no]

# poison_pls_no, pls, NPB = read_attack_data()
# unsorted_pl_no = read_attack_result()

for unsorted in unsorted_pl_no:
	if unsorted in poison_pls_no:
		poison_pls_no.remove(unsorted)

eps_total = [0] * NPB
for pl_no in poison_pls_no:
	eps_total = [eps_total[i] + pls[pl_no][i] for i in range(NPB)]

datablocks = random_draw_datablocks(N=NPB, n=1000)
sens = 1
sum_list = []
for pl_no in poison_pls_no:
	s = []
	# print(pls[pl_no])
	for i in range(NPB):
		if pls[pl_no][i] > 0:
			c = count_with_dp(datablocks[i], mu=0, b=sens/pls[pl_no][i])
			s.append(c * pls[pl_no][i] / eps_total[i])
		else:
			s.append(0)
	sum_list.append(s)

sum_list2 = [0] * NPB
for s in sum_list:
	sum_list2 = [sum_list2[i] + s[i] for i in range(NPB)]

sum_dp = sum(sum_list2)
sum_rl = sum([count(datablock) for datablock in datablocks])

print('%.4f'%(sum_dp - sum_rl))
