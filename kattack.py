#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import copy
from chooseK import gen_2dim_array, brute_force, greedy, dp, repair

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

## k : the attacker can only insert k poisoned pipelines
def k_attack(k: int, sim_arg: tuple) -> tuple:
	_, _, NPB, normal_pls, _ = sim_arg
	n = k + len(normal_pls)
	m = NPB

	alpha = 0.001

	# eps_U_list = gen_2dim_array(n, m)
	eps_U_list = return_eps_U_list(alpha, k, sim_arg)
	for eps_U in eps_U_list:
		for i in eps_U:
			print("%.4f"%i, end=" ")
		print()

	row_list_k = greedy(eps_U_list, n, m, k)
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
			normal_pls[row][i] = eps_U_list[row][i] + alpha
	fill_in_poison_pls_by_summation()

	for pl in normal_pls:
		for demand in pl:
			print('%.4f'%demand, end=" ")
		print()
	# return normal_pls, row_list_k
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

	# step = float(input())
	sim_arg = (eps_Global, first_NPL, NPB, normal_pls, poison_pls)
	pls, poison_pls_no = k_attack(5, sim_arg)

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

