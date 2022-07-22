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

def PrintPipelines(pls: list[list[int|float]]):
	for pl in pls:
		print(["%.2f"%item for item in pl])

class Allocation:
	def __init__(self, eps_Global: float, N: int, NPB: int, pls: list[list[int|float]]):
		self.eps_Global = eps_Global
		self.N = N
		self.NPB = NPB
		self.pls = pls

		self.ds_id_list = []
		self.atkable_list = []
		self.__GenDSIndexList() # dominant share index list
		self.__GenAttackableList() # attackable list

	def __GenDSIndexList(self):
		for pl in self.pls:
			self.ds_id_list.append(pl.index(max(pl)))

	def __GenAttackableList(self):
		for pl_index in range(len(self.pls)):
			if self.pls[pl_index][self.ds_id_list[pl_index]] > 2 * self.eps_Global / self.N:
				self.atkable_list.append(True)
			else:
				if sum(self.pls[pl_index]) > self.eps_Global * self.NPB / self.N:
					self.atkable_list.append(True)
				else:
					self.atkable_list.append(False)

	def _OptimalAllocation(self,
			dpfsys: dpf.DPF,
			block_pls: list[list[int|float]],
			rklist: list[int],
			verbose=False):
		## Insertion
		rklist.sort()
		for rid in rklist:
			block_pls.insert(rid, [alpha] * self.NPB)
		K = len(rklist)
		block_pls = block_pls[:rklist[K-1]+1]

		## Get unallocated budget list
		unallocated_budget_list = []
		for ts in range(rklist[0] - dpfsys.timestamp):
			dpf.pre_Allocation_one(dpfsys, block_pls[ts], False)
			unallocated_budget_list.append(copy.deepcopy(dpfsys.eps_U))

		## when atkable_list change, go into loop again
		## with all parameters restore.
		def _LoopAllTimestamp(dpfsys: dpf.DPF, pls: list[list], unallocated_budget_list: list[list]):
			## list of tuple(v1, v2, v3)
			## \param v1 pipeline row index
			##				v2 pipeline dominant share block index
			##				v3 dominant share value - alpha
			poisoned_ds_list: list[tuple[int, int, float]] = [(-1, -1, self.eps_Global)] * self.NPB

			def _BackFilling(_rklist_index: int, _ds_index: int, _prv_pl_index: int, _delta: float):
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
					return _BackFilling(_rklist_index-1, _ds_index, _cur_pl_index, _delta)
				## Limit exceeds, cannot fill in anymore
				elif _rklist_index == 0:
					pls[_cur_pl_index][_ds_index] = _cmp_value
					return False

				assert(0)

			def _Timestamp(ts: int, rklist_index: int):
				pointer_pl_index = rklist[rklist_index]
				atkable_flag = True

				## Allocation
				dpfsys.OnPipelineArrival(pls[ts])
				unallocated_budget_list.append(dpfsys.eps_U)
				while True:
					finished_pls = dpfsys.OnSchedulerTimer()

					## Apply attack
					for finished_pl in reversed(finished_pls):
						if not self.atkable_list[finished_pl]:
							continue

						## Set dominant share for the current pipeline
						ds_index = self.ds_id_list[finished_pl]
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

						if _BackFilling(rklist_index, ds_index, ts, delta) == False:
							## If there is no pipeline after, then set 0 of the corresponding block
							if ts == 0:
								break
							atkable_flag = False
							old_pl_index, _, _ = poisoned_ds_list[rklist_index]
							self.atkable_list[old_pl_index] = False
							print("Allocation Failed!")
							break

					## Exit loop condition
					if not atkable_flag or len(finished_pls) == 0:
						break

				## fill in the last attack pipeline
				## the final result should sub a small number
				## for the compensation of caculation
				if atkable_flag and ts == len(block_pls)-1:
					for bid in range(self.NPB):
						if dpfsys.eps_U[bid] <= 2 * self.eps_Global / self.N:
							pls[ts][bid] = 0
							continue
						if pls[ts][bid] > alpha:
							flag = _BackFilling(K-2, bid, ts, pls[ts][bid])
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
			rng_low = rklist[0]
			rng_high = rklist[len(rklist)-1] + 1
			for ts in range(rng_low, rng_high):
				if ts in rklist:
					rklist_index += 1
					assert(ts == rklist[rklist_index])
				flag = _Timestamp(ts, rklist_index)
				if flag == False:
					return False, pls
			return True, pls
		## End of loop_alltimestamp

		while True:
			flag, new_pls = _LoopAllTimestamp(
				copy.deepcopy(dpfsys),
				copy.deepcopy(block_pls),
				copy.deepcopy(unallocated_budget_list)
			)
			if verbose:
				print("\nPring pipelines")
				for no in range(self.N):
					print(["%.2f"%d for d in new_pls[no]])
			if flag == True:
				block_pls = new_pls
				break

		return block_pls

	def BlockAllocation(self, dpfsys: dpf.DPF, rng: tuple, K: int):
		assert(K > 1)
		rng_low, rng_high = rng

		pl_index = rng_low
		rklist = []
		while pl_index < rng_high:
			dpf_copy, finished_pls = dpf.pre_Allocation_one(copy.deepcopy(dpfsys), self.pls[pl_index])

			finished_atkable = []
			for finished_pl in finished_pls:
				if self.atkable_list[finished_pl] == True:
					finished_atkable.append(finished_pl)

			canrunlist = []
			if finished_atkable != []:
				for finished_pl in finished_atkable:
					dpf_copy.deComplete(self.pls[finished_pl], finished_pl)
				for wp_pl_index, wp_pl in dpf_copy.wp.items():
					if dpf_copy.CanRun(wp_pl):
						canrunlist.append(wp_pl_index)
				if pl_index in canrunlist:
					canrunlist.remove(pl_index)
				ds_min = self.eps_Global
				for finished_pl in canrunlist:
					ds_index = self.ds_id_list[finished_pl]
					if ds_min >= self.pls[finished_pl][ds_index]:
						ds_min = self.pls[finished_pl][ds_index] - alpha
				atk_pl = [ds_min if ds_min < dpf_copy.eps_U[j] else dpf_copy.eps_U[j] for j in range(self.NPB)]
				rklist.append(pl_index)
				K -= 1
				self.pls.insert(pl_index, atk_pl)
				self.ds_id_list.insert(pl_index, ds_min)
				self.atkable_list.insert(pl_index, False)

			if K == 0:
				break
			dpf.pre_Allocation_one(dpfsys, self.pls[pl_index])
			pl_index += 1

		return rklist

	def OverallAllocation(self, K: int):
		dpfsys = dpf.DPF(self.eps_Global, self.N, self.NPB)
		piece = float(self.N) / float(K)
		one_piece = int(piece * 2)
		return

def main():
	eps_Global, N, NPB, benign_pls = readdata()
	alloc = Allocation(eps_Global, N, NPB, copy.deepcopy(benign_pls),)
	dpfsys = dpf.DPF(eps_Global, N, NPB)
	rng = 0, len(benign_pls)
	rklist = alloc.BlockAllocation(copy.deepcopy(dpfsys), rng, 2)
	print(rklist)
	benign_pls = alloc._OptimalAllocation(dpfsys, benign_pls, rklist)
	PrintPipelines(benign_pls)

if __name__ == '__main__':
	main()
