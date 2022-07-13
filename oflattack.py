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

def atkable(sim_arg, k, rklist):
	eps_Global, N, NPB, pls = sim_arg

	# rklist should be sorted
	for rid in rklist:
		pls.insert(rid, [alpha] * NPB)

	dpfsys = DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()

	wp = {}
	index = 0
	while index < N-k:
		wp[index] = pls[index]
		dpfsys.OnPipelineArrival(pls[index])
		dpfsys.OnSchedulerTimer(wp)
		index += 1
	
	def pre_allocation_one(dpfsys, wp, index, flag: bool) -> list:
		if flag:
			wp[index] = pls[index]
		dpfsys.OnPipelineArrival(pls[index])
		return dpfsys.OnSchedulerTimer(wp)

	def gen_dominantshare_block_id_list(pls, N, NPB) -> list:
		ds_id_list = []
		for i in range(N):
			maxid = 0
			for j in range(0, NPB):
				if pls[i][j] > pls[i][maxid]:
					maxid = j
			ds_id_list.append(maxid)
		return ds_id_list
	ds_id_list = gen_dominantshare_block_id_list(pls, N, NPB)

	rklist_no = -1
	fillin_block_id_list_list = [[]] * k
	fillin_content_list = [eps_Global] * k
	while index < N:
		flag = True # pipeline is benign pipeline
		if index in rklist:
			rklist_no += 1
			flag = False # pipeline is poisoned pipeline

		new_finished = pre_allocation_one(copy.deepcopy(dpfsys), copy.deepcopy(wp), index, flag)

		if len(new_finished) > 0:
			fillin_block_id_list = fillin_block_id_list_list[rklist_no]
			fillin_content = fillin_content_list[rklist_no]
			for finished_pl_no in new_finished:
				ds_id = ds_id_list[finished_pl_no]
				ds_value = pls[finished_pl_no][ds_id]
				fillin_block_id_list.append(ds_id)
				if fillin_content > ds_value:
					fillin_content = ds_value - alpha
			# fillin_block_id_list_list[rklist_no] = fillin_content_list
			fillin_content_list[rklist_no] = fillin_content

			cur_poison_pl = pls[rklist[rklist_no]]
			for block_id in fillin_block_id_list:
				cur_poison_pl[block_id] = fillin_content

		wp[index] = pls[index]
		dpfsys.OnPipelineArrival(pls[index])
		dpfsys.OnSchedulerTimer(pls[index])
		index += 1

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
