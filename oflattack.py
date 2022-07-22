#!/bin/python
# vim:ts=2:sw=2:noet

import ipdb
import random
import dpf
import copy
import chooseK as ck

alpha = 0.01

def return_eps_U_list(sim_arg: tuple) -> list[list[float]]:
	eps_Global, N, NPB, benign_pls = sim_arg
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	eps_U_list = []

	# Simulation
	for i in range(len(benign_pls)):
		dpfsys.OnPipelineArrival(benign_pls[i])
		dpfsys.OnSchedulerTimer()
		eps_U_list.append(copy.deepcopy(dpfsys.eps_U))

	return eps_U_list

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
	pls_file = open('benign_pls.csv')
	lines = pls_file.readlines()
	benign_pls = []
	for line in lines:
		line = line.replace('\n', '')
		benign_pls.append([float(item) for item in line.split("\t")])
	return 30.0, 30, 10, benign_pls

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
	eps_Global, N, _, pls = sim_arg
	atkable_list = []
	for i in range(N): # what if there is no poisoned pipeline in the end
		if pls[i][ds_id_list[i]] > eps_Global / N:
			atkable_list.append(True)
		else:
			atkable_list.append(False)
	return atkable_list

def allocation(sim_arg: tuple, rklist: list[int], K: int=3, verbose=True):
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
		dpf.pre_Allocation_one(dpfsys, pls, verbose)
		unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))

	## get block id number for every pipeline's Dominant Share
	ds_id_list = gen_dominantshare_block_id_list(pls, N, NPB)

	## get ATKABLE list of pipelines
	atkable_list = gen_atkable(sim_arg, ds_id_list)

	## when atkable_list change, go into loop again
	## with all parameters restore.
	def loop_alltimestamp(dpfsys: dpf.DPF, pls: list[list], unallocated_budget_list: list[list]):
		## list of tuple(v1, v2, v3)
		## \param v1 pipeline row index
		##				v2 pipeline dominant share block index
		##				v3 dominant share value - alpha
		poisoned_ds_list: list[tuple[int, int, float]] = [(-1, -1, eps_Global)] * NPB

		def backtracking(_rklist_index: int, _ds_index: int, _prv_pl_index: int, _delta: float):
			if verbose:
				print("backtracking(", _rklist_index, _ds_index, _prv_pl_index, "%.2f"%_delta, ")")

			if _rklist_index < 0:
				print("Error Failed!")
				assert(0)

			## add delta to the poisoned pipeline
			_cur_pl_index = rklist[_rklist_index]
			_budget = unallocated_budget_list[_cur_pl_index][_ds_index] + pls[_cur_pl_index][_ds_index]
			pls[_cur_pl_index][_ds_index] += _delta

			if verbose:
				print(_cur_pl_index, ["%.2f"%item for item in pls[_cur_pl_index]])
				print("unallocated_budget_list")
				for budget_list in unallocated_budget_list:
					print(["%.2f"%ub for ub in budget_list])

			## JUDGE if the value has exceed its limit
			## get dominant share of the pipeline _cur_pl_index
			_, _, _track_ds_value = poisoned_ds_list[_rklist_index]

			## compare dominant share value with unallocated budget
			_cmp_value = 0
			if _track_ds_value > _budget:
				_cmp_value = _budget
			else:
				_cmp_value = _track_ds_value

			## change the history budget record
			for _ts in range(_cur_pl_index+1, _prv_pl_index):
				unallocated_budget_list[_ts][_ds_index] -= _delta
				assert(unallocated_budget_list[_ts][_ds_index] >= 0)

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
				pls[_cur_pl_index][_ds_index] = _cmp_value
				return False

			assert(0)

		def timestamp(ts: int, rklist_index: int):
			pointer_pl_index = rklist[rklist_index]
			atkable_flag = True

			## Allocation
			dpfsys.OnPipelineArrival(pls[ts])
			unallocated_budget_list.append(dpfsys.eps_U)
			while True:
				finished_pls = dpfsys.OnSchedulerTimer()

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
					dpfsys.deComplete(pls[finished_pl], finished_pl)
					dpfsys.eps_U[ds_index] -= delta

					if backtracking(rklist_index, ds_index, ts, delta) == False:
						## If there is no pipeline after, then set 0 of the corresponding block
						if ts == 0:
							break
						atkable_flag = False
						old_pl_index, _, _ = poisoned_ds_list[rklist_index]
						atkable_list[old_pl_index] = False
						print("Allocation Failed!")
						break

				## Exit loop condition
				if not atkable_flag or len(finished_pls) == 0:
					break

			## fill in the last attack pipeline
			## the final result should sub a small number
			## for the compensation of caculation
			if atkable_flag and ts == N-1:
				for bid in range(NPB):
					if dpfsys.eps_U[bid] <= 2 * eps_Global / N:
						pls[ts][bid] = 0
						continue
					if pls[ts][bid] > alpha:
						flag = backtracking(K-2, bid, ts, pls[ts][bid])
						if not flag:
							pls[ts][bid] = 0
						else:
							pls[ts][bid] = dpfsys.eps_U[bid] - alpha
					else:
						pls[ts][bid] = dpfsys.eps_U[bid]

			unallocated_budget_list.pop()
			unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))
			return atkable_flag

		rklist_index = -1
		for ts in range(rklist[0], N):
			if ts in rklist:
				rklist_index += 1
				assert(ts == rklist[rklist_index])
			flag = timestamp(ts, rklist_index)
			if flag == False:
				return False, pls
		return True, pls
	## End of loop_alltimestamp

	while True:
		flag, new_pls = loop_alltimestamp(
			copy.deepcopy(dpfsys),
			copy.deepcopy(pls),
			copy.deepcopy(unallocated_budget_list)
		)
		if verbose:
			print("\nPring pipelines")
			for no in range(N):
				print(["%.2f"%d for d in new_pls[no]])
		if flag == True:
			pls = new_pls
			break

	return pls

class Allocation:
	def __init__(self, eps_Global, N, NPB, pls, K):
		self.ds_id_list = [] # dominant share index list
		self.atkable_list = [] # attackable list
		self.eps_Global = eps_Global
		self.N = N
		self.NPB = NPB
		self.pls = pls
		self.K = K

	def block_allocation(self, dpfsys: dpf.DPF, pls: list[list[float]], rng: tuple, K: int):
		assert(K > 1)
		rng_low, rng_high = rng

		pl_index = rng_low
		while pl_index < rng_high:
			dpf_copy, finished_pls = dpf.pre_Allocation_one(copy.deepcopy(dpfsys), pls[pl_index])

			finished_atkable = []
			for finished_pl in finished_pls:
				if self.atkable_list[finished_pl] == True:
					finished_atkable.append(finished_pl)

			canrunlist = []
			if finished_atkable != []:
				for finished_pl in finished_atkable:
					dpf_copy.deComplete(pls[finished_pl], finished_pl)
				for wp_pl_index, wp_pl in dpf_copy.wp.items():
					if dpf_copy.CanRun(wp_pl):
						canrunlist.append(wp_pl_index)
				if pl_index in canrunlist:
					canrunlist.remove(pl_index)
				ds_min = self.eps_Global
				for finished_pl in canrunlist:
					if ds_min < self.ds_id_list[finished_pl]:
						ds_min = self.ds_id_list[finished_pl]
				atk_pl = [ds_min if ds_min < dpf_copy.eps_U[j] else dpf_copy.eps_U[j] for j in range(self.NPB)]
				pls.insert(pl_index, atk_pl)
				self.ds_id_list.insert(pl_index, ds_min)
				self.atkable_list.insert(pl_index, False)

			dpf.pre_Allocation_one(dpfsys, pls[pl_index])
			pl_index += 1

		return

	def _GenAttackableList(self, pls):
		for pl_index in range(self.N):
			if pls[pl_index][self.ds_id_list[pl_index]] > 2 * self.eps_Global / self.N:
				self.atkable_list.append(True)
			else:
				if sum(pls[pl_index]) > self.eps_Global * self.NPB / self.N:
					self.atkable_list.append(True)
				else:
					self.atkable_list.append(False)

	def _GenDSIndexList(self, pls: list[list[float]]):
		for pl in pls:
			self.ds_id_list.append(pl.index(max(pl)))

	def total_allocation(self, sim_arg: tuple, K: int):
		eps_Global, N, NPB, pls = sim_arg
		dpfsys = dpf.DPF(eps_Global, N, NPB)
		return

def main():
	eps_Global, N, NPB, benign_pls = readdata()

	pls = benign_pls
	sim_arg = eps_Global, N, NPB, pls
	# rklist = list(range(N-2*k+1, N, 2))
	# pls = allocation(sim_arg, rklist, True)
	# sim_arg = eps_Global, N, NPB, pls
	print(dpf.Simulation(sim_arg))
	# print(["%.2f"%sum([pls[rid][bid] for rid in rklist]) for bid in range(NPB)])

if __name__ == '__main__':
	main()
