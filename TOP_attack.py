#!/bin/python
# vim:ts=2:sw=2:noet

from math import ceil

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

def block_slave(step: float, sim_arg: tuple) -> tuple:
	eps_Global, first_NPL, NPB, normal_pls, poison_pls = sim_arg
	assert(len(poison_pls) == 1)

	step_sys = eps_Global / first_NPL
	beta = ceil(step / step_sys)
	alpha = 0.01
	poison_pl = poison_pls[0]
	poison_pls = []
	block_index = 0
	step -= alpha * (NPB - 1)
	while True:
		flag = [item >= step for item in poison_pl]
		if sum(flag) == 0:
			poison_pls.append(poison_pl)
			break

		new_pl = [alpha] * NPB
		new_pl[block_index] = min(step, poison_pl[block_index])
		poison_pl[block_index] -= new_pl[block_index]

		block_index = (block_index + 1) % NPB

		if beta < NPB:
			for i in range(beta, NPB):
				new_pl[i] = min(step, poison_pl[i])
				poison_pl[i] -= new_pl[i]

		poison_pls.append(new_pl)

		if beta > NPB:
			for _ in range(NPB, beta):
				poison_pls.append([alpha] * NPB)

	return poison_pls + normal_pls, list(range(len(poison_pls)))

