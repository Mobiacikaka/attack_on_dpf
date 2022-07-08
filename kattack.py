#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import random
import dpf
import copy
from chooseK import gen_2dim_array, brute_force, greedy, dp, repair

alpha = 0.001

def brute_force_with_kinsert(sim_arg: tuple, k: int) -> tuple:
	eps_Global, first_NPL, NPB, benign_pls = sim_arg

	dpfsys = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()
	wp = {}
	maxeps_U = []
	maxindex = 0

	def pre_allocation(dpfsys: DPF, wp: dict, k: int, index: int) -> list[float]:
		for i in range(k):
			pl = [alpha for _ in range(dpfsys.NPB)]
			wp[index] = pl
			index += 1
			dpfsys.OnPipelineArrival(pl)
			dpfsys.OnSchedulerTimer(wp)
		return dpfsys.eps_U

	# Simulation
	for i in range(len(benign_pls)):
		cureps_U = pre_allocation(copy.deepcopy(dpfsys), copy.deepcopy(wp), k, i)
		if sum(cureps_U) > sum(maxeps_U):
			maxeps_U = cureps_U
			maxindex = i
		wp[i] = benign_pls[i]
		dpfsys.OnPipelineArrival(benign_pls[i])
		dpfsys.OnSchedulerTimer(wp)

	pls = benign_pls
	poison_pls_no = []
	# insert poison pipelines
	for i in list(range(k-1)):
		pls.insert(maxindex + i, [alpha for _ in range(NPB)])
		poison_pls_no.append(maxindex + i)
	pls.insert(maxindex + k-1, maxeps_U)
	poison_pls_no.append(maxindex + k-1)

	return pls, poison_pls_no

def gendata() -> tuple:
	eps_Global	= 10.0
	first_NPL		= 10
	NPB					= 10
	benign_pls	= []
	for _ in range(first_NPL * 4):
		step = eps_Global / first_NPL
		pl = [random.uniform(step * 0.25, step * 0.75) for _ in range(NPB)]
		# print(["%.2f"%item for item in pl])
		benign_pls.append(pl)

	return eps_Global, first_NPL, NPB, benign_pls

if __name__ == '__main__':
	eps_Global, first_NPL, NPB, benign_pls = gendata()
	sim_arg = eps_Global, first_NPL, NPB, benign_pls
	finish_num = len(dpf.Simulation(sim_arg))
	print("finish_num: ", finish_num)

	pls, poison_pls_no = brute_force_with_kinsert(sim_arg, 3)
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
