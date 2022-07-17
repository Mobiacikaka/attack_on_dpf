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
	for ts in range(rklist[0]):
		dpf.pre_Allocation_one(dpfsys, wp, pls, ts, verbose)
		unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))

	## get block id number for every pipeline's Dominant Share
	ds_id_list = gen_dominantshare_block_id_list(pls, N, NPB)

	## get ATKABLE list of pipelines
	atkable_list = gen_atkable(sim_arg, ds_id_list)

	## when atkable_list change, go into loop again
	## with all parameters restore.
	def loop_alltimestamp(dpfsys: dpf.DPF, wp: dict, pls: list[list], unallocated_budget_list: list[list]):
		## list of tuple(v1, v2, v3)
		## \param v1 pipeline row index
		##				v2 pipeline dominant share block index
		##				v3 dominant share value - alpha
		poisoned_ds_list: list[tuple[int, int, float]] = [(-1, -1, 0)] * 3

		def timestamp(ts: int, rklist_index: int):
			pointer_pl_index = rklist[rklist_index]
			poisoned_pl = pls[pointer_pl_index]
			atkable_flag = True

			## Allocation
			wp[ts] = pls[ts]
			dpfsys.OnPipelineArrival(pls[ts])
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
				for finished_pl in reversed(finished_pls):
					if not atkable_list[finished_pl]:
						continue

					## Set dominant share for the current pipeline
					ds_index = ds_id_list[finished_pl]
					if finished_pl < pointer_pl_index:
						new_ds_value = pls[finished_pl][ds_index] - alpha
						old_pl_index, _, old_ds_value = poisoned_ds_list[rklist_index]
						if old_pl_index == -1 or old_ds_value > new_ds_value:
							poisoned_ds_list[rklist_index] = finished_pl, ds_index, new_ds_value

					## ATTACK
					delta = dpfsys.eps_U[ds_index] + alpha

					## Adjust dpfsys and wp
					print()
					print("eps_U", ["%.2f"%ub for ub in dpfsys.eps_U])
					dpfsys.deComplete(wp, pls[finished_pl], finished_pl)
					print("eps_U", ["%.2f"%ub for ub in dpfsys.eps_U])
					dpfsys.eps_U[ds_index] -= delta
					unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))

					## TODO: JUDGE poisoned_pl[ds_index] legal or not
					def backtracking(_rklist_index: int, _ds_index: int, _prv_pl_index: int, _delta: float):
						## add delta to the poisoned pipeline
						_cur_pl_index = rklist[_rklist_index]
						pls[_cur_pl_index][_ds_index] += _delta
						print(_cur_pl_index, ["%.2f"%item for item in pls[_cur_pl_index]])

						## change the history budget record
						for _ts in range(_cur_pl_index, _prv_pl_index):
							unallocated_budget_list[_ts][_ds_index] -= _delta

						## JUDGE if the value has exceed its limit
						## get dominant share of the pipeline _cur_pl_index
						_track_pl_index, _track_db_index, _track_ds_value = poisoned_ds_list[_rklist_index]
						assert(_track_pl_index != -1)

						## compare dominant share value with unallocated budget
						_cmp_value = 0
						if _track_ds_value > unallocated_budget_list[_cur_pl_index][_ds_index]:
							_cmp_value = unallocated_budget_list[_cur_pl_index][_ds_index]
						else:
							_cmp_value = _track_ds_value

						## Return True if demand is below the limit
						if pls[_cur_pl_index][_ds_index] <= _cmp_value:
							return True

						## Limit exceeds, fill in the previous poisoned pipeline
						if _rklist_index > 0:
							_delta = pls[_cur_pl_index][_ds_index] - _cmp_value
							pls[_cur_pl_index][_ds_index] = _cmp_value
							return backtracking(_rklist_index-1, _ds_index, _cur_pl_index, _delta)
						## Limit exceeds, cannot fill in anymore
						elif _rklist_index == 0:
							return False

						assert(0)

					if verbose:
						print(rklist_index, ds_index, ts, "%.2f"%delta)
					if backtracking(rklist_index, ds_index, ts, delta) == False:
						## If there is no pipeline after, then set 0 of the corresponding block
						if ts == 0:
							break
						atkable_flag = False
						old_pl_index, _, _ = poisoned_ds_list[rklist_index]
						atkable_list[old_pl_index] = False
						print("Allocation Failed!")
						break
					unallocated_budget_list.pop()

				## Exit loop condition
				if not atkable_flag:
					break

			unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))
			return atkable_flag

		rklist_index = -1
		for ts in range(rklist[0], N):
			if ts in rklist:
				rklist_index += 1
				assert(ts == rklist[rklist_index])
			flag = timestamp(ts, rklist_index)
			if flag == False:
				for pl in pls:
					print(["%.2f"%item for item in pl])
				return False, []
		for pl in pls:
			print(["%.2f"%d for d in pl])
		return True, pls
	
	count = 0
	while count < 1:
		count += 1
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
