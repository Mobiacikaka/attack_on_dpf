#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import random
import dpf
import copy

alpha = 0.01
k = 3

def return_eps_U_list(sim_arg: tuple) -> list[list[float]]:
	eps_Global, N, NPB, benign_pls = sim_arg
	dpf = DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpf.OnDataBlockCreation()
	wp = {}
	eps_U_list = []

	# Simulation
	for i in range(len(benign_pls)):
		wp[i] = benign_pls[i]
		dpf.OnPipelineArrival(benign_pls[i])
		dpf.OnSchedulerTimer(wp)
		eps_U_list.append(copy.deepcopy(dpf.eps_U))

	return eps_U_list

def brute_force_with_kinsert(sim_arg: tuple, k: int) -> tuple:
	eps_Global, N, NPB, benign_pls = sim_arg

	dpfsys = DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()
	wp = {}
	maxeps_U = []
	maxindex = 0

	def pre_allocation(dpfsys: DPF, wp: dict, k: int, index: int) -> list[float]:
		for i in range(k):
			pl = [alpha] * dpfsys.NPB
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
		pls.insert(maxindex + i, [alpha] * NPB)
		poison_pls_no.append(maxindex + i)
	pls.insert(maxindex + k-1, maxeps_U)
	poison_pls_no.append(maxindex + k-1)

	return pls, poison_pls_no

def gendata() -> tuple:
	eps_Global	= 10.0
	N						= 10
	NPB					= 10
	benign_pls	= []
	for _ in range(N * 3):
		pl = [random.expovariate(1.0) for _ in range(NPB)]
		benign_pls.append(pl)
	return eps_Global, N, NPB, benign_pls

def atkable(sim_arg, k):
	eps_Global, N, NPB, pls = sim_arg

	wp = {}
	ts = 0
	dpfsys = DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()
	for pl in pls:
		wp[ts] = pl
		dpfsys.OnPipelineArrival(pl)
		finished = dpfsys.OnSchedulerTimer(wp)
		print(finished)
		ts += 1
		if ts >= N:
			break

if __name__ == '__main__':
	eps_Global, N, NPB, benign_pls = gendata()

	pls = benign_pls
	sim_arg = eps_Global, N, NPB, pls
	eps_U_list = return_eps_U_list(sim_arg)
	finish_num = len(dpf.Simulation(sim_arg))
	for i in range(N):
		print(['%.2f'%item for item in pls[i]])
	print()
	for i in range(N):
		print(['%.2f'%item for item in eps_U_list[i]])
	print("finish_num: ", finish_num)
