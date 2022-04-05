#!/bin/python
# vim:ts=2:sw=2:noet
from dpf import Simulation

def overstep(pl: list, step: float) -> bool:
	for demand in pl:
		if demand > step:
			return True
	return False

def divide_pl(pl: list, step: float) -> tuple:
	new_pl = []
	for i in range(len(pl)):
		tmp = 0
		if pl[i] > step:
			tmp = step
		else:
			tmp = pl[i]
		new_pl.append(tmp)
		pl[i] -= tmp
	return pl, new_pl

def gen_div_poison_pls(pl: list, step: float) -> list:
	pls = []
	while True:
		new_pl = []
		for i in range(len(pl)):
			new_pl.append( min(pl[i], step) )
			pl[i] -= min(pl[i], step)
		if sum(new_pl) == 0:
			break
		pls.append(new_pl)
	return pls

def insert_top(pls: list, poison_pls: list) -> tuple:
	return poison_pls + pls, list(range(len(poison_pls)))

# def yield_attack(pls: list, poison_pls: list, step_sys: float) -> tuple:
def yield_attack(
	poison_pls,
	sim_arg: tuple[float, int, int, list[list[float]]],
):
	eps_Global, first_NPL, NPB, pls = sim_arg
	finish_pls_no = Simulation(eps_Global, first_NPL, NPB, pls)
	print(finish_pls_no)
	# assert(0)
	return [], []

# def attack(pls: list, step_div: float, step_sys: float, poison_pls_no: list=[0]) -> tuple:
def attack(
	step_div: float, 
	poison_pls_no: list, 
	sim_arg: tuple[float, int, int, list[list[float]]],
):
	# TODO: multiple pipelines
	assert(len(poison_pls_no) == 1)

	eps_Global, first_NPL, NPB, pls = sim_arg

	# generate divided poisoned pipelines
	poison_pls = []
	for i in poison_pls_no:
		poison_pls += gen_div_poison_pls(pls[i], step_div)
	# pop up poisoned pipelines from origin pls
	poison_pls_no.sort()
	for i in range(len(poison_pls_no), 0, -1):
		pls.pop(poison_pls_no[i-1])

	# attack
	sim_arg = (eps_Global, first_NPL, NPB, pls)
	return yield_attack(poison_pls, sim_arg)
	# return insert_top(pls, poison_pls)

eps_Global= float(input())
first_NPL	= int(input())
NPB	= int(input())
NPL	= int(input())

pls = []
for _ in range(NPL):
	line = input()
	pls.append([float(i) for i in line.split()])

step = float(input())
sim_arg = (eps_Global, first_NPL, NPB, pls)
pls, poison_pls_no = attack(step_div=step, poison_pls_no=[0], sim_arg=sim_arg)

print(eps_Global)
print(first_NPL)
print(NPB)
print(len(pls))
for item in pls:
	for item2 in item:
		print('%.4f'%item2, end=" ")
	print()

for pl_no in poison_pls_no:
	print(pl_no, end=" ")
print()
