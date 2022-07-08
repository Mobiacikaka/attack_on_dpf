#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import random
import dpf
import copy
from chooseK import gen_2dim_array, brute_force, greedy, dp, repair

# acquire eps_U in all time
def return_eps_U_list(alpha: float, k: int, sim_arg: tuple) -> list[list[float]]:
	eps_Global, first_NPL, NPB, benign_pls = sim_arg
	pls = [ [alpha]*NPB ] * k + benign_pls

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
	_, _, NPB, benign_pls = sim_arg
	n = k + len(benign_pls)
	m = NPB

	alpha = 0.001

	# eps_U_list = gen_2dim_array(n, m)
	eps_U_list = return_eps_U_list(alpha, k, sim_arg)
	row_list_k = greedy(eps_U_list, n, m, k)

	def compress_rowlist(row_list_k, eps_U_list):
		ulist = [0 for _ in NPB]
		i = 0
		while i < len(row_list_k):
			tmp_ulist = ulist
			rid = row_list_k[i]
			ulist = [max(ulist[j], eps_U_list[rid][j]) for j in range(NPB)]
			if ulist != tmp_ulist:
				row_list_k.remove(rid)
				i -= 1
			i += 1
	compress_rowlist(row_list_k, eps_U_list)

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
			benign_pls.insert(0, [alpha] * NPB)
		for row in row_list_k:
			benign_pls.insert(row, [alpha] * NPB)

		for i in range(NPB):
			row = max_value_row[i]
			benign_pls[row][i] = eps_U_list[row][i] + alpha
	fill_in_poison_pls_by_summation()

	return benign_pls, poison_pls_no

def gendata() -> tuple:
	eps_Global	= 10.0
	first_NPL		= 10
	NPB					= 10
	benign_pls	= []
	for _ in range(first_NPL * 2):
		step = eps_Global / first_NPL
		pl = [random.uniform(step * 0.5, step * 1.1) for _ in range(NPB)]
		# print(["%.2f"%item for item in pl])
		benign_pls.append(pl)

	return eps_Global, first_NPL, NPB, benign_pls

if __name__ == '__main__':
	eps_Global, first_NPL, NPB, benign_pls = gendata()
	sim_arg = eps_Global, first_NPL, NPB, benign_pls
	finish_num = len(dpf.Simulation(sim_arg))
	print("finish_num: ", finish_num)

	pls, poison_pls_no = k_attack(5, sim_arg)
	print(poison_pls_no)
	sim_arg = eps_Global, first_NPL, NPB, benign_pls
	finish_pls_no = dpf.Simulation(sim_arg)
	finish_num = len(finish_pls_no)
	for item in poison_pls_no:
		if item in finish_pls_no:
			finish_num -= 1
	print("finish_num: ", finish_num)

# TODO: maybe wrong that all poison pipelines are calculated from
# a static analyze instead of a dynamic analyzation.
