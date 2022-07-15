#!/bin/python
# vim:ts=2:sw=2:noet

import random
import dpf
import copy

alpha = 0.01
k = 3

def return_eps_U_list(sim_arg: tuple) -> list[list[float]]:
	eps_Global, N, NPB, benign_pls = sim_arg
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()
	wp = {}
	eps_U_list = []

	# Simulation
	for i in range(len(benign_pls)):
		wp[i] = benign_pls[i]
		dpfsys.OnPipelineArrival(benign_pls[i])
		dpfsys.OnSchedulerTimer(wp)
		eps_U_list.append(copy.deepcopy(dpfsys.eps_U))

	return eps_U_list

def brute_force_with_kinsert(sim_arg: tuple, k: int) -> tuple:
	eps_Global, N, NPB, benign_pls = sim_arg

	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()
	wp = {}
	maxeps_U = []
	maxindex = 0

	def pre_allocation(dpfsys: dpf.DPF, wp: dict, k: int, index: int) -> list[float]:
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

def readdata() -> tuple[float, int, int, list[list[int|float]]]:
	pls_file = open('/tmp/benign_pls')
	lines = pls_file.readlines()
	benign_pls = []
	for line in lines:
		line = line.replace('\n', '')
		benign_pls.append([float(item) for item in line.split("\t")])
	return 10.0, 10, 10, benign_pls

def gen_dominantshare_block_id_list(pls, N, NPB) -> list:
	ds_id_list = []
	for i in range(N):
		maxid = 0
		for j in range(0, NPB):
			if pls[i][j] > pls[i][maxid]:
				maxid = j
		ds_id_list.append(maxid)
	return ds_id_list

def gen_atkable(sim_arg, ds_id_list) -> list[bool]:
	eps_Global, N, NPB, pls = sim_arg
	atkable_list = []
	step = eps_Global / N
	for i in range(N-2): # what if there is no poisoned pipeline in the end
		if pls[i][ds_id_list[i]] > 2*step:
			atkable_list.append(True)
		else:
			atkable_list.append(False)
	if pls[N-2][ds_id_list[N-2]] > step:
		atkable_list.append(True)
	atkable_list.append(False)
	return atkable_list

def allocation2(sim_arg: tuple, rklist: list[int], verbose=True):
	eps_Global, N, NPB, pls = sim_arg

	## Insertion
	rklist.sort()
	for rid in rklist:
		pls.insert(rid, [alpha] * NPB)

	## Get unallocated budget list
	dpfsys = dpf.DPF(eps_Global, N, NPB)
	wp = {}
	unallocated_budget_list = []
	for i in range(rklist[0]):
		dpf.pre_Allocation_one(dpfsys, wp, pls, i, verbose)
		unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))

	## get block id number for every pipeline's Dominant Share
	ds_id_list = gen_dominantshare_block_id_list(pls, N, NPB)

	## get ATKABLE list of pipelines
	atkable_list = gen_atkable(sim_arg, ds_id_list)

	## when atkable_list change, go into loop again
	## with all parameters restore.
	def loop_alltimestamp(dpfsys: dpf.DPF, wp: dict, pls: list[list], unallocated_budget_list: list[list]):
		poisoned_ds_list = {}

		def timestamp(index: int, rklist_index: int):
			current_pl_index = rklist[rklist_index]
			poisoned_pl = pls[current_pl_index]
			atkable_flag = True

			## Allocation
			wp[index] = pls[index]
			dpfsys.OnPipelineArrival(pls[index])
			while True:
				## Allocation
				finished_pls = dpfsys.OnSchedulerTimer(wp)

				## Exit condition
				flag = True
				for finished_pl in finished_pls:
					if atkable_list[finished_pl] == True:
						flag = False
				if flag:
					break

				## Apply attack
				for finished_pl in finished_pls:
					if not atkable_list[finished_pl]:
						continue

					## Set dominant share for the current pipeline
					ds_index = ds_id_list[finished_pl]
					if finished_pl < current_pl_index:
						new_ds = pls[finished_pl][ds_index]
						if poisoned_ds_list[current_pl_index] >= pls[new_ds]:
							poisoned_ds_list[current_pl_index] = new_ds - alpha

					## ATTACK
					delta = dpfsys.eps_U[ds_index] + alpha
					poisoned_pl[ds_index] += delta

					## TODO: JUDGE poisoned_pl[ds_index] legal or not
					def backtracking(rklist_index, ds_index, prv_index, delta):
						bt_pl_index = rklist[rklist_index] # in backtracking
						for index_ in range(bt_pl_index, prv_index):
							unallocated_budget_list[index_][ds_index] -= delta
						pl = pls[bt_pl_index]
						delta = pl[ds_index] - poisoned_ds_list[bt_pl_index]
						if delta <= 0:
							return True
						if rklist_index == 0:
							assert(0)
						else:
							pls[rklist[rklist_index-1]][ds_index] += delta
							return backtracking(rklist_index-1, ds_index, bt_pl_index, delta)
						return False
					if backtracking(rklist_index, ds_index, index, delta) == False:
						atkable_flag = False
						break

					## Adjust dpfsys and wp
					dpfsys.deComplete(wp, pls[finished_pl], finished_pl)
					dpfsys.eps_U[ds_index] -= delta

				## Exit loop condition
				if not atkable_flag:
					break

			unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))
			return atkable_flag

		rklist_index = -1
		for index in range(rklist[0], N):
			if index in rklist:
				rklist_index += 1
				assert(index == rklist[rklist_index])
			flag = timestamp(index, rklist_index)
			if flag == False:
				return False, []
		return True, pls
	
	while True:
		flag, new_pls = loop_alltimestamp(
			copy.deepcopy(dpfsys), 
			copy.deepcopy(wp), 
			copy.deepcopy(pls), 
			copy.deepcopy(unallocated_budget_list)
		)
		if flag == True:
			pls = new_pls
			break

if __name__ == '__main__':
	eps_Global, N, NPB, benign_pls = readdata()

	pls = benign_pls
	sim_arg = eps_Global, N, NPB, pls
	rklist = list(range(N-2*k+1, N, 2))
	allocation2(sim_arg, rklist)
