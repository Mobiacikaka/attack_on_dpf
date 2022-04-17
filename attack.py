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

def top_attack(step: float, poison_pls_no:list, sim_arg: tuple) -> tuple:
	assert(len(poison_pls_no) == 1)

	_, _, _, pls = sim_arg

	# generate divided poisoned pipelines
	poison_pls = []
	for i in poison_pls_no:
		poison_pls += gen_div_poison_pls(pls[i], step)
	# pop up poisoned pipelines from origin pls
	poison_pls_no.sort()
	for i in range(len(poison_pls_no), 0, -1):
		pls.pop(poison_pls_no[i-1])

	return poison_pls+pls, list(range(len(poison_pls)))

def slavery_attack(step: float, poison_pls_no: list, sim_arg: tuple) -> tuple:
	assert(len(poison_pls_no) == 1 and poison_pls_no[0] == 0)

	eps_Global, first_NPL, NPB, pls = sim_arg
	step_sys = eps_Global / first_NPL

	incre = 0.01 # increment
	rb_index = 0 # rotate block index
	poison_pls = []
	poison_pl = pls[0]
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

	return poison_pls + pls, list(range(len(poison_pls)))

def yield_attack(step: float, poison_pls_no: list, sim_arg: tuple) -> tuple:
	new_pls = []
	poison_pls_no = []

	def simulate_dpf():
		eps_Global, first_NPL, NPB, pls = sim_arg

		dpf = DPF(eps_Global, first_NPL)
		for _ in range(NPB):
			dpf.OnDataBlockCreation()

		wp = {}
		foresee = 3
		poison_pl = pls[0]
		pls_no = 0
		index = 0
		lower_bound = step * NPB / 2
		while True:
			if sum(poison_pl) == 0:
				break
			if index >= first_NPL:
				# TODO:
				assert(0)
				for _pls_no in range(pls_no, len(pls)):
					new_pls.append(pls[_pls_no])
				break

			def get_most_profit_index() -> int:
				nonlocal index, wp, dpf
				_index = copy.deepcopy(index) # index of waiting pipelines
				_wp = copy.deepcopy(wp)
				_dpf = copy.deepcopy(dpf)

				_max_sum = sum(_dpf.eps_U)
				# best insert poisition after pls[pls_no]
				_max_insert_no = copy.deepcopy(pls_no)

				# pre-allocate to pipelines
				for _pls_no in range(pls_no, pls_no+foresee):
					_wp[_index] = pls[_pls_no]
					_dpf.OnPipelineArrival(pls[_pls_no])
					_dpf.OnSchedulerTimer(_wp)
					_sum_i = sum(_dpf.eps_U)
					# TODO: criteria - sum or single
					if _max_sum < _sum_i:
						_max_sum = _sum_i
						_max_insert_no = _pls_no + 1
					_index += 1
				return _max_insert_no
			insert_pos = get_most_profit_index()

			# TODO: skip if small than the lower bound

			# allocate base on the criteria
			def insert_base_on_simulation():
				nonlocal pls_no, index

				for _pls_no in range(pls_no, insert_pos):
					new_pls.append(pls[_pls_no])
					wp[index] = pls[_pls_no]
					dpf.OnPipelineArrival(pls[_pls_no])
					dpf.OnSchedulerTimer(wp)
					index += 1

				new_pl = dpf.eps_U
				dpf.OnPipelineArrival(new_pl)
				new_pl = dpf.eps_U
				wp[index] = new_pl
				dpf.OnSchedulerTimer(wp)
				new_pls.append(new_pl)
				poison_pls_no.append(index)
				index += 1
				pls_no = insert_pos
			insert_base_on_simulation()

			# fill the rest if possible
			def fill_rest():
				nonlocal dpf, poison_pl, NPB
				flag = False
				for i in range(NPB):
					if poison_pl[i] >= dpf.eps_G[i] - dpf.eps_C[i]:
						flag = True
				if flag:
					return

				# 
				assert(0)
			fill_rest()

	simulate_dpf()

	return new_pls, poison_pls_no

def sneak_attack(step: float, poison_pls_no: list, sim_arg: tuple) -> tuple:
	pls, poison_pls_no = top_attack(step, poison_pls_no, sim_arg)

	# first simulation
	# find out what pipelines need to be modify
	def simulate_dpf():
		nonlocal pls, poison_pls_no
		optim = []
		return optim
	optim = simulate_dpf()

	# intergrate the pipelines which need to 
	# be optimized into one pipeline
	remain = [sum(item)]

	return [], []

eps_Global= float(input())
first_NPL	= int(input())
NPB	= int(input())
NPL	= int(input())

pls = []
for _ in range(NPL):
	line = input()
	pls.append([float(i) for i in line.split()])

poison_pls_no = [int(i) for i in input().split()]
assert(len(poison_pls_no) == 1 and poison_pls_no[0] == 0)

step = float(input())
sim_arg = (eps_Global, first_NPL, NPB, pls)
pls, poison_pls_no = slavery_attack(step=step, poison_pls_no=poison_pls_no, sim_arg=sim_arg)

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
