#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
from functools import cmp_to_key
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

def dp_choose_k(k: int, matrix: list[list[float]], n: int, m: int) -> list:
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

## k : the attacker can only insert k poisoned pipelines
def k_attack(k: int, sim_arg: tuple) -> tuple:
	eps_Global, first_NPL, NPB, normal_pls, _ = sim_arg

	alpha = 0.001

	eps_U_list = return_eps_U_list(alpha, k, sim_arg)
	for eps_U in eps_U_list:
		for i in eps_U:
			print("%.4f"%i, end=" ")
		print()

	max_U_index = [0] * NPB
	for i in range(1, first_NPL):
		for j in range(NPB):
			if eps_U_list[i][j] > eps_U_list[max_U_index[j]][j]:
				max_U_index[j] = i

	print(max_U_index)

	def __gen_row_dict(max_U_index: list, NPB: int) -> dict[int, list]:
		row_dict = dict.fromkeys(max_U_index, [])
		for block_index in range(NPB):
			row = max_U_index[block_index]
			if len(row_dict[row]) == 0:
				row_dict[row] = [block_index]
			else:
				row_dict[row].append(block_index)
		return row_dict

	def brute_force_summation() -> list:
		nonlocal eps_U_list, max_U_index, k, alpha, NPB
		poison_pls = []
		for _ in range(k):
			poison_pls.append([alpha] * NPB)
		row_dict = __gen_row_dict(max_U_index, NPB)
		row_list = [row for row, _ in row_dict.items()]

		row_list_k = []
		perfect_sum = 0
		if len(row_list) <= k:
			row_list_k = row_list
		else:
			import itertools as it
			for row_list_k_tmp in it.combinations(row_list, k):
				row_list_k_tmp = list(row_list_k_tmp)
				combi = [0] * NPB
				for row in row_list_k_tmp:
					combi = max(combi, eps_U_list[row])
				if sum(combi) > perfect_sum:
					perfect_sum = sum(combi)
					row_list_k = row_list_k_tmp

		for j in range(NPB):
			for i in range(len(row_list_k)):
				pass
		return []

	def maximize_perfect_block_number() -> list:
		nonlocal eps_U_list, max_U_index, k, alpha, NPB
		poison_pls = []
		for _ in range(k):
			poison_pls.append([alpha] * NPB)
		row_dict = __gen_row_dict(max_U_index, NPB)
		row_list = [row for row, _ in row_dict.items()]

		# sort row_list
		def cmp_row(x: int, y: int):
			nonlocal row_dict, eps_U_list
			def cmp_row_by_perfect_numbers(x: int, y: int):
				nonlocal row_dict
				if len(row_dict[x]) > len(row_dict[y]):
					return 1
				elif len(row_dict[x]) < len(row_dict[y]):
					return -1
				else:
					return 0
			def cmp_row_by_sumation(x: int, y: int):
				nonlocal row_dict, eps_U_list
				x_list = [eps_U_list[x][item] for item in row_dict[x]]
				y_list = [eps_U_list[y][item] for item in row_dict[y]]
				if sum(x_list) > sum(y_list):
					return 1
				elif sum(x_list) < sum(y_list):
					return -1
				else:
					return 0
			def cmp_row_by_no(x: int, y: int):
				if x > y:
					return 1
				elif x < y:
					return -1
				else:
					return 0
			_perfect_numbers_flag = cmp_row_by_perfect_numbers(x, y)
			_sumation_flag = cmp_row_by_sumation(x, y)
			_no_flag = cmp_row_by_no(x, y)
			if _perfect_numbers_flag > 0:
				return 1
			elif _perfect_numbers_flag < 0:
				return -1
			else:
				if _sumation_flag > 0:
					return 1
				elif _sumation_flag < 0:
					return -1
				else:
					if _no_flag > 0:
						return 1
					elif _no_flag < 0:
						return -1
					else:
						assert(0)
						return 0
		sorted(row_list, key=cmp_to_key(cmp_row))

		# choose k row
		row_list_k = row_list[:k]
		for i in range(len(row_list_k)):
			row = row_list_k[i]
			for block_index in row_dict[row]:
				poison_pls[i][block_index] = eps_U_list[row][block_index]
				row_dict[row].remove(block_index)

		# fill in the imperfect block
		for row, block_list in row_dict.items():
			if block_list == []:
				pass
			for block_index in block_list:
				best_row_index = 0
				for i in range(1, len(row_list_k)):
					if eps_U_list[row_list_k[i]][block_index] > eps_U_list[row_list_k[best_row_index]][block_index]:
						best_row_index = i
				poison_pls[best_row_index][block_index] = eps_U_list[row_list_k[best_row_index]][block_index]

		# insert poison pipelines into the normal
		return poison_pls

	def greedy_summation() -> list:
		nonlocal eps_U_list, max_U_index, k, alpha, NPB
		poison_pls = []
		for _ in range(k):
			poison_pls.append(copy.deepcopy([alpha] * NPB))
		row_dict = __gen_row_dict(max_U_index, NPB)
		row_list = [row for row, _ in row_dict.items()]

		def cmp_row(x: int, y: int):
			nonlocal row_dict, eps_U_list
			def cmp_row_by_sumation(x: int, y: int):
				nonlocal row_dict, eps_U_list
				x_list = [eps_U_list[x][item] for item in row_dict[x]]
				y_list = [eps_U_list[y][item] for item in row_dict[y]]
				if sum(x_list) > sum(y_list):
					return 1
				elif sum(x_list) < sum(y_list):
					return -1
				else:
					return 0
			def cmp_row_by_no(x: int, y: int):
				if x > y:
					return 1
				elif x < y:
					return -1
				else:
					return 0
			_sumation_flag = cmp_row_by_sumation(x, y)
			_no_flag = cmp_row_by_no(x, y)
			if _sumation_flag > 0:
				return 1
			elif _sumation_flag < 0:
				return -1
			else:
				if _no_flag > 0:
					return 1
				elif _no_flag < 0:
					return -1
				else:
					assert(0)
					return 0
		sorted(row_list, key=cmp_to_key(cmp_row))

		# choose k row
		row_list_k = row_list[:k]
		for i in range(len(row_list_k)):
			row = row_list_k[i]
			for block_index in row_dict[row]:
				poison_pls[i][block_index] = eps_U_list[row][block_index]
				row_dict[row].remove(block_index)

		# fill in the rest
		for row, block_list in row_dict.items():
			if block_list == []:
				pass
			for block_index in block_list:
				best_row_index = 0
				for i in range(1, len(row_list_k)):
					row = row_list_k[i]
					best_row = row_list_k[best_row_index]
					if eps_U_list[row][block_index] > eps_U_list[best_row][block_index]:
						best_row_index = i
				best_row = row_list_k[best_row_index]
				poison_pls[best_row_index][block_index] = eps_U_list[best_row][block_index]

		return poison_pls

	def max_min() -> list:
		nonlocal eps_U_list, max_U_index, k, alpha, NPB
		poison_pls = []
		return poison_pls

	poison_pls = []
	for _ in range(k):
		poison_pls.append([alpha] * NPB)

	row_list_k = dp_choose_k(k, eps_U_list, len(eps_U_list), NPB)
	def fill_in_poison_pls_by_summation():
		for _ in range(k-len(row_list_k)):
			normal_pls.insert(0, [alpha] * NPB)
		for row in row_list_k:
			normal_pls.insert(row, [alpha] * NPB)

		max_value_row = [0] * NPB
		max_value = [0] * NPB
		for row in row_list_k:
			for j in range(NPB):
				if eps_U_list[row][j] > max_value[j]:
					max_value[j] = eps_U_list[row][j]
					max_value_row[j] = row
		
		for i in range(NPB):
			row = max_value_row[i]
			normal_pls[row][i] = eps_U_list[row][i]

	fill_in_poison_pls_by_summation()
	for pl in normal_pls:
		for demand in pl:
			print('%.4f'%demand, end=" ")
		print()
	# return poison_pls + normal_pls, list(range(len(poison_pls)))
	return [], []
