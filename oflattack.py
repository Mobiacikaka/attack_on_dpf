#!/bin/python
# vim:ts=2:sw=2:noet
from decimal import Decimal as dec
import random
import dpf
import copy

from dpf import dec_format
alpha = dec(dec_format % (1 / 100))

## Utility Functions
def return_eps_U_list(sim_arg: tuple) -> list[list[dec]]:
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

def gendata(eps_Global, N, NPB) -> tuple:
	benign_pls	= []
	for _ in range(N * 2):
		pl = []
		for _ in range(NPB):
			rnd = random.expovariate(1.0)
			pl.append(dec(dec_format % rnd))
		benign_pls.append(pl)
	return eps_Global, N, NPB, benign_pls

def readdata(filename: str='benign_pls.csv') -> tuple[float, int, int, list[list[dec]]]:
	pls_file = open(filename)
	lines = pls_file.readlines()
	benign_pls = []
	for line in lines:
		try:
			line = line.replace('\n', '')
			benign_pls.append([dec(item) for item in line.split("\t")])
		except:
			pass
	return float(len(benign_pls)), len(benign_pls), len(benign_pls[0]), benign_pls

def PrintPipeline(pl: list[dec]):
	print([dec_format % item for item in pl])

def PrintPipelines(pls: list[list[dec]], N: int=0):
	if N == 0:
		N = len(pls)
	for i in range(N):
		PrintPipeline(pls[i])

def SumPipelines(pls, list_no: list=[]):
	if len(list_no) == 0:
		list_no = list(range(len(pls)))

	sumpl = dec(0)
	for i in list_no:
		sumpl += sum(pls[i])
	return sumpl

def getDominantShareIDList(pls):
	ds_id_list = []
	for pl in pls:
		ds_id = 0
		for j in range(1, len(pl)):
			if pl[j] > pl[ds_id]:
				ds_id = j
		ds_id_list.append(ds_id)
	return ds_id_list

def MaximizeAllocationAtTS(dpfsys: dpf.DPF, ) -> list[dec]:
	unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
	for j in range(dpfsys.NPB):
		unallocated_eps_list[j] += dpfsys.eps_G[j] / dpfsys.N

	wp = dpfsys.wp
	sorted_pipelines = sorted(list(wp.keys()), key=lambda x: dpfsys.DominantShareList(wp.get(x)))
	canrunflag = False # check if exist waiting pipeline can run
	poisoned_pl = []
	for bplno in sorted_pipelines:
		if sum(unallocated_eps_list) <= sum(poisoned_pl):
			break # the allocation afterwards cannot be higher

		bpl = wp.get(bplno, None)
		assert(bpl != None)
		if not dpfsys.CanRun(bpl, unallocated_eps_list):
			continue

		canrunflag = True
		ds = max(bpl)
		tmp_poisoned_pl = []
		for j in range(dpfsys.NPB):
			if ds <= unallocated_eps_list[j]:
				tmp_poisoned_pl.append(ds - alpha)
			else:
				tmp_poisoned_pl.append(unallocated_eps_list[j])

		if sum(tmp_poisoned_pl) > sum(poisoned_pl):
			poisoned_pl = tmp_poisoned_pl

		for j in range(dpfsys.NPB):
			unallocated_eps_list[j] -= bpl[j]

	if not canrunflag:
		poisoned_pl = unallocated_eps_list

	return poisoned_pl


## Allocation Functions
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
			print(ts, finished_pls_seq)
			print(pls[ts])
			print(dpfsys.eps_U)
			for pl_no in finished_pls_seq:
				print(pls[pl_no])
			assert(0)

	return pls, poisoned_list

def DynamicSeqAttack0(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)
	step = dec(dec_format % (eps_Global / N))

	ts = -1
	poisoned_list = []
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	k1 = 0
	k2 = K
	while k2 > 0:
		ts += 1
		insert_flag = False

		unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
		for j in range(NPB):
			unallocated_eps_list[j] += step
		unallocated_eps_list2 = copy.deepcopy(unallocated_eps_list)
		wp = copy.deepcopy(dpfsys.wp)
		wp2 = copy.deepcopy(wp)
		if ts + k2 < N:
			wp[ts] = pls[ts]
		sorted_pipelines = sorted(list(wp.keys()), key=lambda x: dpfsys.DominantShareList(wp.get(x)))
		for seq in sorted_pipelines:
			pl = wp.get(seq)
			assert(pl != None)

			if not dpfsys.CanRun(pl, unallocated_eps_list):
				continue

			def AttackAble(seq):
				ds_id = ds_id_list[seq]
				assert(pl != None)
				return ((N-ts-k2)/k2) < pl[ds_id]

			if AttackAble(seq):
				insert_flag = True
				break
			else:
				for j in range(NPB):
					unallocated_eps_list[j] -= pl[j]

		unallocated_eps_list = unallocated_eps_list2
		wp = wp2
		sorted_pipelines = sorted(list(wp.keys()), key=lambda x: dpfsys.DominantShareList(wp.get(x)))
		ds = eps_Global
		if insert_flag:
			for seq in sorted_pipelines:
				pl = wp.get(seq)
				assert(pl != None)

				if not dpfsys.CanRun(pl, unallocated_eps_list):
					continue

				def AttackAble(seq):
					ds_id = ds_id_list[seq]
					assert(pl != None)
					return ((N-ts-k2)/k2) < pl[ds_id]

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
			print(ts, finished_pls_seq)
			for pl_no in finished_pls_seq:
				PrintPipeline(pls[pl_no])
			PrintPipeline(dpfsys.eps_U)
			assert(0)

	return pls, poisoned_list

def DynamicSeqAttack(sim_arg: tuple, K: int, notattackablelist: list=[]):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)
	step = dec(dec_format % (eps_Global / N))

	ts = -1
	poisoned_list = []
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	k1 = 0
	k2 = K
	while k2 > 0:
		ts += 1

		unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
		for j in range(NPB):
			unallocated_eps_list[j] += step

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
					restbudget = (N - ts - 1) * step + unallocated_eps_list[j]
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
						restbudget = (N - ts - 1) * step + unallocated_eps_list[j]
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

def multiDynamicSeqAttack(sim_arg: tuple, K: int, times: int=2):
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
			poisoned_pl = MaximizeAllocationAtTS(dpfsys)
			pls.insert(ts, poisoned_pl)

		## Do Normal Allocation
		dpfsys.AddToWaiting(pls[ts])
		dpfsys.OnPipelineArrival(pls[ts])
		finished_pls_seq = dpfsys.OnSchedulerTimer()
		if ts in poisoned_list:
			assert(ts in finished_pls_seq)

	return pls, poisoned_list

def BlockAttack(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)

	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	k1 = 0
	k2 = K
	start = 0
	end = 0
	poisoned_list = []
	while k2 > 0:
		## Find The Best Insert Position In The Next Several Pipelines
		start = end
		end += (N - K) / K
		dpfsys2 = copy.deepcopy(dpfsys)
		poisoned_pl = []
		insert_ts = 0
		for ts2 in range(int(start)+k1, int(end)+k1+1):
			if ts2 >= N:
				break

			tmp_poisoned_pl = MaximizeAllocationAtTS(dpfsys2)
			if sum(tmp_poisoned_pl) > sum(poisoned_pl):
				poisoned_pl = tmp_poisoned_pl
				insert_ts = ts2

			dpfsys2.AddToWaiting(pls[ts2])
			dpfsys2.OnPipelineArrival(pls[ts2])
			dpfsys2.OnSchedulerTimer()

		## Insert
		pls.insert(insert_ts, poisoned_pl)
		ds_id_list.insert(insert_ts, 0)
		poisoned_list.append(insert_ts)
		k1 += 1
		k2 -= 1

		## Do Normal Allocation
		for ts in range(int(start)+k1-1, int(end)+k1):
			if ts >= N:
				break
			dpfsys.AddToWaiting(pls[ts])
			dpfsys.OnPipelineArrival(pls[ts])
			finished_pls_seq = dpfsys.OnSchedulerTimer()
			# print(f'{ts}:eps\t', dpfsys.eps_U)
			if ts == insert_ts:
				# print(f'{ts}\t', pls[ts])
				assert(insert_ts in finished_pls_seq)

	return pls, poisoned_list

def BlockAttack2(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) >= N)

	ds_id_list = getDominantShareIDList(pls)

	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, NPB=NPB)
	k1 = 0
	k2 = K
	start = 0
	end = 0
	poisoned_list = []
	insert_ts = -1
	while k2 > 0:
		## Find The Best Insert Position In The Next Several Pipelines
		start = insert_ts + 1
		end += (N - K) / K
		dpfsys2 = copy.deepcopy(dpfsys)
		poisoned_pl = []
		for ts2 in range(start, int(end)+k1+1):
			if ts2 >= N:
				break

			tmp_poisoned_pl = MaximizeAllocationAtTS(dpfsys2)
			if sum(tmp_poisoned_pl) > sum(poisoned_pl):
				poisoned_pl = tmp_poisoned_pl
				insert_ts = ts2

			dpfsys2.AddToWaiting(pls[ts2])
			dpfsys2.OnPipelineArrival(pls[ts2])
			dpfsys2.OnSchedulerTimer()

		## Insert
		pls.insert(insert_ts, poisoned_pl)
		ds_id_list.insert(insert_ts, 0)
		poisoned_list.append(insert_ts)
		k1 += 1
		k2 -= 1

		## Do Normal Allocation
		for ts in range(start, insert_ts+1):
			if ts >= N:
				break
			dpfsys.AddToWaiting(pls[ts])
			dpfsys.OnPipelineArrival(pls[ts])
			finished_pls_seq = dpfsys.OnSchedulerTimer()
			# print(f'{ts}:eps\t', dpfsys.eps_U)
			if ts == insert_ts:
				# print(f'{ts}\t', pls[ts])
				assert(insert_ts in finished_pls_seq)

	return pls, poisoned_list

def main_gen():
	eps_Global, N, NPB, benign_pls = readdata('data.csv')
	# eps_Global, N, NPB, benign_pls = gendata(30.0, 30, 30)
	sim_arg = (eps_Global, N, NPB, benign_pls)
	K = int(0.2 * N)
	K = 7

	def CallFunc(funcname):
		pls, poisoned_list = funcname(copy.deepcopy(sim_arg), K)
		# PrintPipelines(pls, N)
		sim_arg1 = (eps_Global, N, NPB, pls)
		complete = dpf.Simulation(sim_arg1)
		for i in poisoned_list:
			assert(i in complete)
		perc = SumPipelines(pls, poisoned_list) / (N * NPB)
		print('%.4f' % perc, poisoned_list)

	# CallFunc(RandomAttack)
	CallFunc(BlockAttack)
	# CallFunc(BlockAttack2)
	# CallFunc(DynamicATKable)
	# CallFunc(DynamicSeqAttack0)
	CallFunc(DynamicSeqAttack)
	CallFunc(multiDynamicSeqAttack)

def main_read_sim():
	eps_Global, N, NPB, pls = readdata()
	sim_arg = eps_Global, N, NPB, pls
	print(dpf.Simulation(sim_arg))

if __name__ == '__main__':
	main_gen()
