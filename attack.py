#!/bin/python
# vim:ts=2:sw=2:noet
from dpf import DPF
from math import ceil
import copy

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

def top_attack(step: float, sim_arg: tuple) -> tuple:
	_, _, _, normal_pls, poison_pls = sim_arg
	assert(len(poison_pls) == 1)

	# generate divided poisoned pipelines
	new_poison_pls = []
	for i in range(len(poison_pls)):
		new_poison_pls += gen_div_poison_pls(poison_pls[i], step)

	return new_poison_pls+normal_pls, list(range(len(new_poison_pls)))

def slavery_attack(step: float, sim_arg: tuple) -> tuple:
	eps_Global, first_NPL, NPB, normal_pls, poison_pls = sim_arg
	assert(len(poison_pls) == 1)

	step_sys = eps_Global / first_NPL
	incre = 0.01 # increment
	rb_index = 0 # rotate block index
	poison_pl = poison_pls[0]
	poison_pls = []
	while True:
		# TODO: break condition
		def break_condition() -> bool:
			nonlocal poison_pl, NPB, step
			flag = True
			for i in range(NPB):
				if poison_pl[i] >= step:
					flag = False
			return flag
		if break_condition() == True:
			break

		# generate new flower-poisoned pipeline
		flower = []
		for i in range(NPB):
			flower.append(min(step, poison_pl[i]))
			poison_pl[i] -= min(step, poison_pl[i])
		poison_pls.append(flower)

		# generate enough leaf-poisoned pipelines
		for i in range(ceil(step/step_sys) - 1):
			leaf = []
			for i in range(NPB):
				addi = step + incre if i == rb_index else incre
				leaf.append(min(poison_pl[i], addi))
				poison_pl[i] -= min(poison_pl[i], addi)
			poison_pls.append(leaf)
			rb_index = (rb_index + 1) % NPB

	return poison_pls + normal_pls, list(range(len(poison_pls)))

def sneak_attack(step: float, sim_arg: tuple) -> tuple:
	pls, poison_pls_no = top_attack(step, sim_arg)

	# first simulation
	# find out what pipelines need to be modify
	def simulate_dpf():
		nonlocal pls, poison_pls_no
		optim = []
		return optim
	optim = simulate_dpf()

	# intergrate the pipelines which need to 
	# be optimized into one pipeline
	# remain = [sum(item)]

	return [], []

def main():
	eps_Global= float(input())
	first_NPL	= int(input())
	NPB	= int(input())

	NPL	= int(input())
	normal_pls = []
	for _ in range(NPL):
		normal_pls.append([float(i) for i in input().split()])

	poison_num = int(input())
	poison_pls = []
	for _ in range(poison_num):
		poison_pls.append([float(i) for i in input().split()])

	step = float(input())
	sim_arg = (eps_Global, first_NPL, NPB, normal_pls, poison_pls)
	pls, poison_pls_no = slavery_attack(step=step, sim_arg=sim_arg)

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

main()
