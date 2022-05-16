#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import copy

# acquire eps_U in all time
def return_eps_U_list(alpha: float, k: int, sim_arg: tuple) -> list[list[float]]:
	eps_Global, first_NPL, NPB, normal_pls, _ = sim_arg
	pls = [ [alpha]*NPB ] * k + normal_pls

	def Simulation():
		nonlocal eps_Global, first_NPL, pls
		dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
		for _ in range(NPB):
			dpf.OnDataBlockCreation()

		wp = {}
		eps_U_list = []
		for i in range(len(pls)):
			wp[i] = pls[i]
			dpf.OnPipelineArrival(pls[i])
			dpf.OnSchedulerTimer(wp)
			eps_U_list.append(copy.deepcopy(dpf.eps_U))

		return eps_U_list

	return Simulation()

def list_max(x: list, y: list) -> list:
	assert(len(x) == len(y))
	return [max(x[i], y[i]) for i in range(len(x))]

def brute_force_choose_k_by_summation(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	import itertools as it

	row_list = list(range(n))
	perfect_max = [0] * m
	perfect_route = []
	for e in it.combinations(row_list, k):
		row_list_k = list(e)
		tmp_max = [0] * m
		for row in row_list_k:
			tmp_max = list_max(tmp_max, matrix[row])
		if sum(tmp_max) > sum(perfect_max):
			perfect_max = tmp_max
			perfect_route = row_list_k
	
	perfect_route.sort()
	return perfect_route

def greedy_choose_k_by_summation(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	sum_list = {}
	for i in range(n):
		sum_list[i] = sum(matrix[i])
	
	sorted_list = sorted(sum_list, key=lambda x: sum_list[x], reverse=True)
	row_list_k = sorted_list[:k]

	print(row_list_k)
	row_list_k.sort()
	return row_list_k

def dp_choose_k_by_summation(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	perfect_route = []
	perfect_max = [0] * m

	for _ in range(k):
		tmp_max_value = sum(perfect_max)
		tmp_max_index = -1
		for i in range(n):
			cycle_max = list_max(perfect_max, matrix[i])
			cycle_sum = sum(cycle_max)
			if cycle_sum > tmp_max_value:
				tmp_max_value = cycle_sum
				tmp_max_index = i
		if tmp_max_index >= 0:
			perfect_route.append(tmp_max_index)
			perfect_max = list_max(perfect_max, matrix[tmp_max_index])

	perfect_route.sort()
	return perfect_route

def dp_choose_k_by_max_min(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	perfect_route = []
	perfect_max = [0] * m

	for _ in range(k):
		tmp_min_value = sorted(perfect_max)
		tmp_max_index = -1
		for i in range(n):
			cycle_max = list_max(perfect_max, matrix[i])
			cycle_min_value = sorted(cycle_max)
			if cycle_min_value > tmp_min_value:
				tmp_min_value = cycle_min_value
				tmp_max_index = i
		if tmp_max_index >= 0:
			perfect_route.append(tmp_max_index)
			perfect_max = list_max(perfect_max, matrix[tmp_max_index])
	
	perfect_route.sort()
	return perfect_route

## k : the attacker can only insert k poisoned pipelines
def k_attack(k: int, sim_arg: tuple) -> tuple:
	_, _, NPB, normal_pls, _ = sim_arg

	alpha = 0.001

	eps_U_list = return_eps_U_list(alpha, k, sim_arg)
	for eps_U in eps_U_list:
		for i in eps_U:
			print("%.4f"%i, end=" ")
		print()

	row_list_k = dp_choose_k_by_max_min(k, eps_U_list, len(eps_U_list), NPB)
	print(row_list_k)
	def fill_in_poison_pls_by_summation():
		max_value_row = [0] * NPB
		max_value = [0] * NPB
		for row in row_list_k:
			for j in range(NPB):
				if eps_U_list[row][j] > max_value[j]:
					max_value[j] = eps_U_list[row][j]
					max_value_row[j] = row
		
		# brute-force and greedy will return extra and useless row
		# clear these useless rows is very important
		i = 0
		while i < len(row_list_k):
			if row_list_k[i] not in max_value_row:
				row_list_k.pop(i)
				i -= 1
			i += 1
		row_list_k.sort()
		for _ in range(k-len(row_list_k)):
			normal_pls.insert(0, [alpha] * NPB)
		for row in row_list_k:
			normal_pls.insert(row, [alpha] * NPB)

		for i in range(NPB):
			row = max_value_row[i]
			normal_pls[row][i] = eps_U_list[row][i]
	fill_in_poison_pls_by_summation()

	for pl in normal_pls:
		for demand in pl:
			print('%.4f'%demand, end=" ")
		print()
	# return normal_pls, row_list_k
	return [], []
