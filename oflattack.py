#!/bin/python
# vim:ts=2:sw=2:noet

from ast import Call
from pickle import NONE
import ipdb
import statistics
import random

from prompt_toolkit.styles import default_pygments_style
import dpf
import copy

alpha = 1.0/100

## Utility Functions
def return_eps_U_list(sim_arg: tuple) -> list[list[float]]:
	eps_Global, N, NPB, benign_pls = sim_arg
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	eps_U_list = []

	# Simulation
	for pl in benign_pls:
		dpfsys.AddToWaiting(pl)
		dpfsys.OnPipelineArrival(pl)
		dpfsys.OnSchedulerTimer()
		eps_U_list.append(copy.deepcopy(dpfsys.eps_U))

	return eps_U_list

def gendata() -> tuple:
	eps_Global	= 30.0
	N						= 30
	NPB					= 30
	benign_pls	= []
	for _ in range(N * 2):
		pl = [float(format(random.expovariate(1.0), ".5")) for _ in range(NPB)]
		benign_pls.append(pl)
	return eps_Global, N, NPB, benign_pls

def readdata() -> tuple[float, int, int, list[list[int|float]]]:
	pls_file = open('benign_pls.csv')
	lines = pls_file.readlines()
	benign_pls = []
	for line in lines:
		try:
			line = line.replace('\n', '')
			benign_pls.append([float(item) for item in line.split("\t")])
		except:
			pass
	return 30.0, 30, 10, benign_pls

def PrintPipeline(pl: list[int|float]):
	print(["%.2f"%item for item in pl])

def PrintPipelines(pls: list[list[int|float]], N: int=0):
	if N == 0:
		N = len(pls)
	for i in range(N):
		PrintPipeline(pls[i])

def SumPipelines(pls, list_no: list=[]):
	if len(list_no) == 0:
		list_no = list(range(len(pls)))

	sumpl = 0
	for i in list_no:
		sumpl += sum(pls[i])
	return sumpl


## Allocation class
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
			ds_value = max(pl)
			ds_index = pl.index(ds_value)
			self.ds_id_list.append((ds_index, ds_value))

	def __GenAttackableList(self):
		self.atkable_list = [False] * len(self.pls)

	def __OptimalAllocation(self,
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
				dpfsys.AddToWaiting(pls[ts])
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

	def __BlockAllocation(self, dpfsys: dpf.DPF, rng: tuple, K: int):
		assert(K > 1)
		rng_low, rng_high = rng
		pls = copy.deepcopy(self.pls[rng_low:rng_high])
		start = 0
		rng_high -= rng_low
		rklist = []
		while K > 0:
			def __LocatePoisonedIndex(dpfsys: dpf.DPF, start: int) -> int:
				nonlocal K
				flag = False
				## Find the first timestamp that a attackable pipeline is allocated
				i = start
				for i in range(start, rng_high):
					pl = pls[i]
					dpfsys.AddToWaiting(pl)
					dpfsys.OnPipelineArrival(pl)
					finished_pls = dpfsys.OnSchedulerTimer()

					for finished_pl in finished_pls:
						if self.atkable_list[finished_pl] == True:
							flag = True
							dpfsys.deComplete(pls[finished_pl], finished_pl)
					if flag:
						if K == 1:
							K -= 1
							rklist.append(i)
							return i+1
						break
				## Get the smallest dominant share(can run) before the index
				if flag:
					## Get CanRun List
					canrunlist = []
					for pl_ts, pl in dpfsys.wp.items():
						if dpfsys.CanRun(pl) and pl_ts < i:
							canrunlist.append(pl_ts)
					## Get the smallest ds in canrunlist
					ds_min = self.eps_Global
					for pl_index in canrunlist:
						ds_index = self.ds_id_list[pl_index]
						ds_value = pls[pl_index][ds_index]
						if ds_value < ds_min:
							ds_min = ds_value
					## Fill in the poisoned pipeline
					poisoned_pl = copy.deepcopy(dpfsys.eps_U)
					for j in range(self.NPB):
						if poisoned_pl[j] >= ds_min:
							poisoned_pl[j] = ds_min - alpha
					pls.insert(i, poisoned_pl)
					rklist.append(i)
					K -= 1
					return i+1
				else:
					assert(0)
				assert(0)
				return 0

			## Main Body of loop
			stop = __LocatePoisonedIndex(copy.deepcopy(dpfsys), start)
			if K == 0:
				break
			for pl in self.pls[start:stop]:
				dpfsys.AddToWaiting(pl)
				dpfsys.OnPipelineArrival(pl)
				dpfsys.OnSchedulerTimer()
			start = stop

		return rklist

	def OverallAllocation(self, K: int):
		dpfsys = dpf.DPF(self.eps_Global, self.N, self.NPB)
		piece = float(self.N) / float(K)
		one_piece = int(piece * 2)
		rng = (0, len(self.pls))
		rklist = self.__BlockAllocation(dpfsys, rng, 2)
		print(rklist)
		return

def getDominantShareIDList(pls):
	ds_id_list = []
	for pl in pls:
		ds_id = 0
		for j in range(1, len(pl)):
			if pl[j] > pl[ds_id]:
				ds_id = j
		ds_id_list.append(ds_id)
	return ds_id_list

def DynamicATKable(sim_arg, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)

	dpfsys = dpf.DPF(eps_Global, N, NPB)
	candi = N - K + 1
	ts = -1
	poisoned_list = []
	while K > 0:
		ts += 1
		candi -= 1
		ctrl = candi / K

		new_dpfsys, finished_pls = dpf.pre_Allocation_one(copy.deepcopy(dpfsys), pls[ts])
		insert_flag = False

		# Check if insert
		for finished_pl in finished_pls:
			ds_value = pls[finished_pl][ds_id_list[finished_pl]]
			if ds_value <= ctrl:
				if finished_pl == ts:
					new_dpfsys.deComplete(pls[finished_pl], finished_pl)
				pass
			else:
				insert_flag = True
				new_dpfsys.deComplete(pls[finished_pl], finished_pl)

		# Min Dominant Share
		dsmi = eps_Global
		for pl_no, pl in new_dpfsys.wp.items():
			ds_value = pl[ds_id_list[pl_no]]
			if pl_no == ts:
				continue
			if not new_dpfsys.CanRun(pl):
				continue
			if ds_value <= ctrl:
				continue
			if ds_value < dsmi:
				dsmi = ds_value

		if ts + K >= N:
			insert_flag = True

		if insert_flag:
			poisoned_pl = copy.deepcopy(new_dpfsys.eps_U)
			for j in range(NPB):
				if poisoned_pl[j] >= dsmi:
					poisoned_pl[j] = dsmi - alpha
			pls.insert(ts, poisoned_pl)
			ds_id_list.insert(ts, 0)
			poisoned_list.append(ts)
			K -= 1
			candi += 1

		dpfsys.AddToWaiting(pls[ts])
		dpfsys.OnPipelineArrival(pls[ts])
		finished_pls_seq = dpfsys.OnSchedulerTimer()
		if insert_flag and ts not in finished_pls_seq:
			print("failed", pls[ts])
			print("spare", dpfsys.eps_U)
			assert(0)

	return pls, poisoned_list

def DynamicSeqAttack0(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)

	ts = -1
	poisoned_list = []
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	k1 = 0
	k2 = K
	while k2 > 0:
		ts += 1

		unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
		for j in range(NPB):
			unallocated_eps_list[j] += eps_Global / N

		sorted_pipelines = sorted(list(dpfsys.wp.keys()), key=lambda x: dpfsys.DominantShareList(dpfsys.wp.get(x)))
		insert_flag = False
		ds = 0
		for seq in sorted_pipelines:
			pl = dpfsys.wp.get(seq)
			assert(pl != None)

			if not dpfsys.CanRun(pl, unallocated_eps_list):
				continue

			def AttackAble(seq):
				ds_id = ds_id_list[seq]
				assert(pl != None)
				ds = pl[ds_id]
				return ((N-ts-k2)/k2) < ds

			if AttackAble(seq):
				insert_flag = True
				ds = pl[ds_id_list[seq]]
				break
			else:
				for j in range(NPB):
					unallocated_eps_list[j] -= pl[j]

		# if there are poisoned pipelines left, insert anyway
		if ts + k2 >= N:
			insert_flag = True
			if sorted_pipelines != []:
				seq = sorted_pipelines[0]
				ds = pls[seq][ds_id_list[seq]]
			else:
				ds = eps_Global
		if insert_flag == True:
			poisoned_pl = []
			for j in range(NPB):
				if unallocated_eps_list[j] >= ds:
					poisoned_pl.append(ds - alpha)
				else:
					poisoned_pl.append(unallocated_eps_list[j])
			pls.insert(ts, poisoned_pl)
			ds_id_list.insert(ts, 0)
			poisoned_list.append(ts)
			k1 += 1
			k2 -= 1

		# Do normal Allocation
		dpfsys.AddToWaiting(pls[ts])
		dpfsys.OnPipelineArrival(pls[ts])
		finished_pls_seq = dpfsys.OnSchedulerTimer()
		if insert_flag and ts not in finished_pls_seq:
			print("failed", pls[ts])
			print("spare", dpfsys.eps_U)
			assert(0)

	return pls, poisoned_list

def DynamicSeqAttack(sim_arg: tuple, K: int, notattackablelist: list=[]):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)

	ts = -1
	poisoned_list = []
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	k1 = 0
	k2 = K
	while k2 > 0:
		ts += 1

		unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
		for j in range(NPB):
			unallocated_eps_list[j] += eps_Global / N

		sorted_pipelines = sorted(list(dpfsys.wp.keys()), key=lambda x: dpfsys.DominantShareList(dpfsys.wp.get(x)))
		insert_flag = False
		ds = 0
		for seq in sorted_pipelines:
			pl = dpfsys.wp.get(seq)
			assert(pl != None)

			if not dpfsys.CanRun(pl, unallocated_eps_list):
				continue

			def AttackAble(seq):
				pl = pls[seq]
				def __JudgeByDominantShare():
					j = ds_id_list[seq]
					restbudget = (N - ts + 1) * eps_Global / N + unallocated_eps_list[j]
					if len(notattackablelist) > 0:
						for i in notattackablelist:
							if i + k1 > ts:
								restbudget -= pls[i+k1][j]
					ds_i = pl[ds_id_list[seq]]
					if restbudget - ds_i * k2 < ds_i:
						return True
					return False
				def __JudgeByAllBlock():
					for j in range(NPB):
						restbudget = (N - ts + 1) * eps_Global / N + unallocated_eps_list[j]
						if len(notattackablelist) != 0:
							assert(0)
						ds_i = pl[ds_id_list[seq]]
						if restbudget - ds_i * k2 < ds_i:
							return True
					return False
				return __JudgeByDominantShare()

			if AttackAble(seq):
				insert_flag = True
				ds = pl[ds_id_list[seq]]
				break
			else:
				for j in range(NPB):
					unallocated_eps_list[j] -= pl[j]

		# if there are poisoned pipelines left, insert anyway
		if ts + k2 >= N:
			insert_flag = True
			if sorted_pipelines != []:
				seq = sorted_pipelines[0]
				ds = pls[seq][ds_id_list[seq]]
			else:
				ds = eps_Global
		if insert_flag == True:
			poisoned_pl = []
			for j in range(NPB):
				if unallocated_eps_list[j] >= ds:
					poisoned_pl.append(ds - alpha)
				else:
					poisoned_pl.append(unallocated_eps_list[j])
			pls.insert(ts, poisoned_pl)
			ds_id_list.insert(ts, 0)
			poisoned_list.append(ts)
			k1 += 1
			k2 -= 1

		# Do normal Allocation
		dpfsys.AddToWaiting(pls[ts])
		dpfsys.OnPipelineArrival(pls[ts])
		finished_pls_seq = dpfsys.OnSchedulerTimer()
		if insert_flag and ts not in finished_pls_seq:
			print("failed", pls[ts])
			print("spare", dpfsys.eps_U)
			assert(0)

	return pls, poisoned_list

def multiDynamicSeqAttack(sim_arg: tuple, K: int, times: int=3):
	eps_Global, N, NPB, pls = sim_arg
	poisoned_list = []
	notattackablelist = []
	pls = []
	for _ in range(times):
		pls, poisoned_list = DynamicSeqAttack(sim_arg=copy.deepcopy(sim_arg), K=K, notattackablelist=notattackablelist)
		complete = dpf.Simulation(sim_arg)
		complete.sort()
		poisoned_list.sort()

		ts = 0
		countbpl = 0
		countppl = 0
		while ts < N:
			if countbpl < len(complete) and ts == complete[countbpl]:
				if countppl < len(poisoned_list) and ts == poisoned_list[countppl]:
					countppl += 1
				else:
					notattackablelist.append(ts - countppl)
				countbpl += 1
			ts += 1
	
	return pls, poisoned_list

def RandomAttack(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(N >= K)

	ds_id_list = getDominantShareIDList(pls)

	poisoned_list = []
	choices = list(range(N))
	for _ in range(K):
		choice = random.choice(choices)
		choices.remove(choice)
		poisoned_list.append(choice)

	poisoned_list.sort()
	dpfsys = dpf.DPF(eps_Global, N, NPB)
	for ts in range(N):

		## Insert Poisoned Pipelines
		if ts in poisoned_list:
			unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
			for j in range(NPB):
				unallocated_eps_list[j] += eps_Global / N
			sorted_pipelines = sorted(list(dpfsys.wp.keys()), key=lambda x: dpfsys.DominantShareList(dpfsys.wp.get(x)))

			poisoned_pl = [0] * NPB
			canrunflag = False
			for bplno in sorted_pipelines:
				if sum(unallocated_eps_list) <= sum(poisoned_pl):
					break
				bpl = dpfsys.wp.get(bplno, None)
				assert(bpl != None)
				if not dpfsys.CanRun(bpl, unallocated_eps_list):
					continue
				canrunflag = True
				ds = bpl[ds_id_list[bplno]]
				new_poisoned_pl = []
				for j in range(NPB):
					if ds <= unallocated_eps_list[j]:
						new_poisoned_pl.append(ds-alpha)
					else:
						new_poisoned_pl.append(unallocated_eps_list[j])
				if sum(new_poisoned_pl) > sum(poisoned_pl):
					poisoned_pl = new_poisoned_pl
				for j in range(NPB):
					unallocated_eps_list[j] -= bpl[j]

			if not canrunflag:
				poisoned_pl = unallocated_eps_list
			pls.insert(ts, poisoned_pl)

		## Do Normal Allocation
		dpfsys.AddToWaiting(pls[ts])
		dpfsys.OnPipelineArrival(pls[ts])
		finished_pls_seq = dpfsys.OnSchedulerTimer()
		if ts in poisoned_list:
			assert(ts in finished_pls_seq)

	return pls, poisoned_list

def main_gen():
	eps_Global, N, NPB, benign_pls = gendata()
	sim_arg = (eps_Global, N, NPB, benign_pls)
	K = int(0.2 * N)

	def CallFunc(funcname):
		pls, poisoned_list = funcname(copy.deepcopy(sim_arg), K)
		# PrintPipelines(pls, N)
		sim_arg1 = (eps_Global, N, NPB, pls)
		complete = dpf.Simulation(sim_arg1)
		for i in poisoned_list:
			assert(i in complete)
		print("%.3f"%(SumPipelines(pls, poisoned_list) / (N * NPB)), poisoned_list)

	CallFunc(RandomAttack)
	CallFunc(DynamicATKable)
	CallFunc(DynamicSeqAttack0)
	CallFunc(DynamicSeqAttack)
	CallFunc(multiDynamicSeqAttack)

def main_read_sim():
	eps_Global, N, NPB, pls = readdata()
	sim_arg = eps_Global, N, NPB, pls
	print(dpf.Simulation(sim_arg))

if __name__ == '__main__':
	main_gen()
