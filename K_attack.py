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
	sorted_list = sorted(list(range(n)), key=lambda x: sum(matrix[x]), reverse=True)
	row_list_k = sorted_list[:k]
	row_list_k.sort()
	return row_list_k

def dp_choose_k_by_summation(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	hist_route = []
	hist_maxvalue = []
	hist_metric = []

	for _ in range(n):
		hist_route.append([])
		hist_maxvalue.append([0] * m)
		hist_metric.append(0)

	def metric(value: list):
		# by summation
		return sum(value)
	
	for _ in range(k):
		prsnt_route = []
		prsnt_maxvalue = []
		prsnt_metric = []
		for i in range(n):
			pivot_index = -1
			pivot_maxvalue = []
			pivot_metric = hist_metric[i]
			for j in range(n):
				cycle_maxvalue = list_max(matrix[i], hist_maxvalue[j])
				cycle_metric = metric(cycle_maxvalue)
				if cycle_metric > pivot_metric:
					pivot_index = j
					pivot_maxvalue = cycle_maxvalue
					pivot_metric = cycle_metric
			if pivot_index >= 0:
				prsnt_route.append(hist_route[pivot_index] + [i])
				prsnt_maxvalue.append(pivot_maxvalue)
				prsnt_metric.append(pivot_metric)
			else:
				prsnt_route.append(hist_route[i])
				prsnt_maxvalue.append(hist_maxvalue[i])
				prsnt_metric.append(hist_metric[i])
		if max(prsnt_metric) == max(hist_metric):
			break
		hist_route = prsnt_route
		hist_maxvalue = prsnt_maxvalue
		hist_metric = prsnt_metric
	
	perfect_index = 0
	for i in range(1, n):
		if hist_metric[i] > hist_metric[perfect_index]:
			perfect_index = i

	perfect_route = hist_route[perfect_index]
	perfect_route.sort()
	return perfect_route

def dp_choose_k_by_summation_kai(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	dp_routes = []
	dp_listmaxs = []
	dp_metrics = []

	for _ in range(k+1):
		dp_route = []
		dp_listmax = []
		dp_metric = []
		for _ in range(n):
			dp_route.append([])
			dp_listmax.append([0] * m)
			dp_metric.append(0)
		dp_routes.append(dp_route)
		dp_listmaxs.append(dp_listmaxs)
		dp_metrics.append(dp_metric)
	
	level_perfectroute = []
	level_perfectlistmax = []
	level_perfectmetric = 0
	for kbar in range(1, k+1):
		for i in range(n):
			pivot_index = -1
			pivot_listmax = []
			pivot_metric = dp_metrics[kbar-1][i]
			for j in range(n):
				cycle_listmax = list_max(matrix[i], dp_listmaxs[kbar-1][j])
				cycle_metric = sum(cycle_listmax)
				if cycle_metric > pivot_metric:
					pivot_index = j
					pivot_listmax = cycle_listmax
					pivot_metric = cycle_metric
			if pivot_index >= 0:
				dp_routes[kbar][i] = dp_routes[kbar-1][pivot_index] + [i]
				dp_listmaxs[kbar][i] = pivot_listmax
				dp_metrics[kbar][i] = pivot_metric
			else:
				dp_routes[kbar][i] = level_perfectroute
				dp_listmaxs[kbar][i] = level_perfectlistmax
				dp_metrics[kbar][i] = level_perfectmetric

		level_perfectroute = []
		level_perfectlistmax = []
		level_perfectmetric = 0
		for i in range(n):
			if level_perfectmetric < dp_metrics[kbar][i]:
				level_perfectroute = dp_routes[kbar][i]
				level_perfectlistmax = dp_listmaxs[kbar][i]
				level_perfectmetric = dp_metrics[kbar][i]

	level_perfectroute.sort()
	return level_perfectroute

def dp_choose_k_by_maxmin(k: int, matrix: list[list[float]], n: int, m: int) -> list:
	hist_route = []
	hist_maxvalue = []
	hist_metric = []

	for _ in range(n):
		hist_route.append([])
		hist_maxvalue.append([0] * m)
		hist_metric.append([0] * m)

	def metric(value: list):
		# by summation
		value.sort()
		return value
	
	for _ in range(k):
		prsnt_route = []
		prsnt_maxvalue = []
		prsnt_metric = []
		for i in range(n):
			pivot = matrix[i]
			pivot_metric = hist_metric[i]
			pivot_index = -1
			for j in range(n):
				cycle_maxvalue = list_max(pivot, hist_maxvalue[j])
				cycle_metric = metric(copy.deepcopy(cycle_maxvalue))
				if cycle_metric > pivot_metric:
					pivot_metric = cycle_metric
					pivot_index = j
			if pivot_index >= 0:
				prsnt_route.append(hist_route[pivot_index] + [i])
				prsnt_maxvalue.append(list_max(matrix[i], hist_maxvalue[pivot_index]))
				prsnt_metric.append(pivot_metric)
			else:
				prsnt_route.append(hist_route[i])
				prsnt_maxvalue.append(hist_maxvalue[i])
				prsnt_metric.append(hist_metric[i])
		if max(prsnt_metric) == max(hist_metric):
			break
		hist_route = prsnt_route
		hist_maxvalue = prsnt_maxvalue
		hist_metric = prsnt_metric
	
	perfect_index = 0
	for i in range(1, n):
		if hist_metric[i] > hist_metric[perfect_index]:
			perfect_index = i

	perfect_route = hist_route[perfect_index]
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

	row_list_k = greedy_choose_k_by_summation(k, eps_U_list, len(eps_U_list), NPB)
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

