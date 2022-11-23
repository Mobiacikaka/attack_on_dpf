#!/usr/bin/python3
# vim:ts=2:sw=2:noet
from decimal import Decimal as dec
import random, numpy
import dpf
import copy
import statistics, time

from dpf import dec_format
alpha = dec(dec_format % (1 / 100))

## Utility Functions
def ReturnFunctionName(funcname):
	return str(funcname).split(' ')[1]

def return_eps_U_list(sim_arg: tuple) -> list:
	eps_Global, N, M, benign_pls = sim_arg
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, M=M)
	eps_U_list = []

	# Simulation
	for pl in benign_pls:
		dpfsys.AddToWaiting(pl)
		dpfsys.OnPipelineArrival(pl)
		dpfsys.OnSchedulerTimer()
		eps_U_list.append(copy.deepcopy(dpfsys.eps_U))

	return eps_U_list

def GenDataset(ratio, N, M, sigma_mice=10.0, sigma_elephant=1.0) -> list:
	assert(sigma_mice >= sigma_elephant)
	benign_pls = []
	for _ in range(N):
		sigma = numpy.random.choice([sigma_mice, sigma_elephant], 1, p=[ratio, 1-ratio])[0]
		pl = []
		for _ in range(M):
			rnd = random.expovariate(sigma)
			pl.append(dec(dec_format % rnd) + alpha)
		benign_pls.append(pl)
	return benign_pls

def ReadDataset(N) -> list:
	benign_pls = []
	for _ in range(N):
		line = input()
		pl_str = line.split('\t')[:-1]
		pl = [dec(dec_format % float(a)) for a in pl_str]
		benign_pls.append(pl)
	return benign_pls

def PrintPipeline(pl: list):
	for item in pl:
		print(float(item), end='\t')
	print()

def PrintPipelines(pls: list, N: int=0):
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

def MaximizeAllocationAtTS(dpfsys: dpf.DPF, ) -> list:
	unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
	for j in range(dpfsys.M):
		unallocated_eps_list[j] += dpfsys.eps_G[j] / dpfsys.N

	wp = dpfsys.wp
	sorted_pipelines = sorted(list(wp.keys()), key=lambda x: dpfsys.DominantShareList(wp.get(x)))
	zeroflag = False
	poisoned_pl = []
	for bplno in sorted_pipelines:
		if sum(unallocated_eps_list) <= sum(poisoned_pl):
			break # the allocation afterwards cannot be higher

		bpl = wp.get(bplno, None)
		assert(bpl != None)
		if not dpfsys.CanRun(bpl, unallocated_eps_list):
			continue

		ds = max(bpl)
		tmp_poisoned_pl = []
		for j in range(dpfsys.M):
			if ds <= unallocated_eps_list[j]:
				tmp_poisoned_pl.append(ds - alpha)
			else:
				tmp_poisoned_pl.append(unallocated_eps_list[j])

		if sum(tmp_poisoned_pl) > sum(poisoned_pl):
			poisoned_pl = tmp_poisoned_pl

		for j in range(dpfsys.M):
			unallocated_eps_list[j] -= bpl[j]
			if unallocated_eps_list[j] == 0:
				zeroflag = True

	if not zeroflag:
		if sum(unallocated_eps_list) > sum(poisoned_pl):
			poisoned_pl = unallocated_eps_list

	return poisoned_pl


## Allocation Functions
def RandomAttack(sim_arg: tuple, K: int):
	eps_Global, N, M, pls = sim_arg
	assert(N >= K)

	poisoned_list = random.sample(list(range(N)), K)
	poisoned_list.sort()

	return pls, poisoned_list

def RandomSeqAttack(sim_arg: tuple, K: int):
	eps_Global, N, M, pls = sim_arg
	assert(N >= K)

	poisoned_list = random.sample(list(range(N)), K)
	poisoned_list.sort()
	dpfsys = dpf.DPF(eps_Global, N, M)
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

def NaiveGreedy(sim_arg: tuple, K: int):
	eps_Global, N, M, pls = sim_arg
	assert(N >= K)

	poisoned_list = []
	k2 = K
	while k2 > 0:
		insert_ts = 0
		max_poisoned_pl = []
		dpfsys = dpf.DPF(eps_Global, N, M)
		for ts in range(N-k2+1):
			if ts not in poisoned_list:
				## Find the best position
				tmp_poisoned_pl = MaximizeAllocationAtTS(dpfsys)
				if sum(tmp_poisoned_pl) > sum(max_poisoned_pl):
					insert_ts = ts
					max_poisoned_pl = tmp_poisoned_pl
			dpfsys.AddToWaiting(pls[ts])
			dpfsys.OnPipelineArrival(pls[ts])
			dpfsys.OnSchedulerTimer()
		pls.insert(insert_ts, max_poisoned_pl)
		for i in range(len(poisoned_list)):
			if poisoned_list[i] >= insert_ts:
				poisoned_list[i] += 1
		poisoned_list.append(insert_ts)
		k2 -= 1
	return pls, poisoned_list

def GreedyFramework(sim_arg: tuple, K: int, method='__Tree_MaxEveryDepth', **kwargs):
	eps_Global, N, M, pls = sim_arg
	assert(len(pls) + K >= N)

	def __Tree_MaxEveryDepth(__pls: list, __poisoned_list: list) -> tuple:
		__pls = copy.deepcopy(__pls)
		__poisoned_list = copy.deepcopy(__poisoned_list)

		for i in range(len(__poisoned_list)):
			__poisoned_list[i] += i

		tmp_sum = dec(0)
		__dpfsys = dpf.DPF(eps_Global, N, M)
		for i in range(N-K+len(__poisoned_list)):
			if i in __poisoned_list:
				tmp_poisoned_pl = MaximizeAllocationAtTS(__dpfsys)
				tmp_sum += sum(tmp_poisoned_pl)
				__pls.insert(i, tmp_poisoned_pl)
			__dpfsys.AddToWaiting(__pls[i])
			__dpfsys.OnPipelineArrival(__pls[i])
			__dpfsys.OnSchedulerTimer()
		return __pls, tmp_sum

	def __Tree_DFS(__pls: list, __poisoned_list: list) -> tuple:
		__pls = copy.deepcopy(__pls)
		__poisoned_list = copy.deepcopy(__poisoned_list)

		for i in range(len(__poisoned_list)):
			__poisoned_list[i] += i

		__dpfsys__ = dpf.DPF(eps_Global, N, M)

		def __DFS(__pls: list, __dpfsys: dpf.DPF, ts: int) -> tuple:
			while ts not in __poisoned_list:
				## Do normal allocation
				__dpfsys.AddToWaiting(__pls[ts])
				__dpfsys.OnPipelineArrival(__pls[ts])
				__dpfsys.OnSchedulerTimer()
				ts += 1
				if ts >= N:
					## The Allocation is done
					return __pls, dec(0)
			## Divide into different Branch
			eps_U = copy.deepcopy(__dpfsys.eps_U)
			for j in range(M):
				eps_U[j] += __dpfsys.eps_G[j] / __dpfsys.N

			wp = __dpfsys.wp
			sorted_pipelines = sorted(list(wp.keys()), key=lambda x: __dpfsys.DominantShareList(wp.get(x)))

			max_pls = []
			max_branch = dec(0)

			for plno in sorted_pipelines:
				pl = __pls[plno]
				if __dpfsys.CanRun(pl, eps_U):
					for j in range(M):
						assert(eps_U[j] >= pl[j])
					## Generate Poisoned Pipeline
					ds = max(pl)
					tmp_poisoned_pl = []
					for j in range(M):
						if ds <= eps_U[j]:
							tmp_poisoned_pl.append(ds - alpha)
						else:
							tmp_poisoned_pl.append(eps_U[j])
					__pls_copy = copy.deepcopy(__pls)
					__dpfsys_copy = copy.deepcopy(__dpfsys)

					## Create Branch
					__pls_copy.insert(ts, tmp_poisoned_pl)
					__dpfsys_copy.AddToWaiting(tmp_poisoned_pl)
					__dpfsys_copy.OnPipelineArrival(tmp_poisoned_pl)
					complete = __dpfsys_copy.OnSchedulerTimer()
					assert(ts in complete)
					__pls_tmp, branch_max_sum = __DFS(__pls_copy, __dpfsys_copy, ts+1)
					branch_max_sum += sum(tmp_poisoned_pl)
					if branch_max_sum > max_branch:
						max_branch = branch_max_sum
						max_pls = __pls_tmp

					## Do Fake Allocation
					for j in range(M):
						assert(eps_U[j] >= pl[j])
						eps_U[j] -= pl[j]
						if eps_U[j] == 0:
							return max_pls, max_branch

			if True:
				__pls_copy = copy.deepcopy(__pls)
				__dpfsys_copy = copy.deepcopy(__dpfsys)
				## Create Branch
				tmp_poisoned_pl = copy.deepcopy(eps_U)
				__pls_copy.insert(ts, tmp_poisoned_pl)
				__dpfsys_copy.AddToWaiting(tmp_poisoned_pl)
				__dpfsys_copy.OnPipelineArrival(tmp_poisoned_pl)
				complete = __dpfsys_copy.OnSchedulerTimer()
				if ts not in complete:
					print(ts, complete)
					print(__dpfsys.eps_U)
					print(eps_U)
					print(__dpfsys_copy.eps_U)
					print(__dpfsys_copy.wp)
				assert(ts in complete)
				__pls_tmp, branch_max_sum = __DFS(__pls_copy, __dpfsys_copy, ts+1)
				branch_max_sum += sum(tmp_poisoned_pl)
				if branch_max_sum > max_branch:
					max_branch = branch_max_sum
					max_pls = __pls_tmp

			return max_pls, max_branch

		return __DFS(__pls, __dpfsys__, 0)

	def __Tree_DFS_depth_limited(__pls: list, __poisoned_list: list, __d: int=1) -> tuple:
		__pls = copy.deepcopy(__pls)
		__poisoned_list = copy.deepcopy(__poisoned_list)

		for i in range(len(__poisoned_list)):
			__poisoned_list[i] += i

		def __DFS_depth_limited(__pls: list, __dpfsys: dpf.DPF, ts: int, depth: int) -> tuple:
			if depth == 0 or len(__poisoned_list) == 0 or ts > max(__poisoned_list):
				return __pls, dec(0)
			while ts not in __poisoned_list:
				if ts >= N:
					return __pls, dec(0)
				## Do normal allocation
				assert(ts == __dpfsys.timestamp)
				__dpfsys.AddToWaiting(__pls[ts])
				__dpfsys.OnPipelineArrival(__pls[ts])
				__dpfsys.OnSchedulerTimer()
				ts += 1
			## Divide into different Branch
			eps_U = copy.deepcopy(__dpfsys.eps_U)
			for j in range(M):
				eps_U[j] += __dpfsys.eps_G[j] / __dpfsys.N

			wp = __dpfsys.wp
			sorted_pipelines = sorted(list(wp.keys()), key=lambda x: __dpfsys.DominantShareList(wp.get(x)))

			max_pls = []
			max_branch = dec(0)

			for plno in sorted_pipelines:
				pl = __pls[plno]
				if __dpfsys.CanRun(pl, eps_U):
					for j in range(M):
						assert(eps_U[j] >= pl[j])
					## Generate Poisoned Pipeline
					ds = max(pl)
					tmp_poisoned_pl = []
					for j in range(M):
						if ds <= eps_U[j]:
							tmp_poisoned_pl.append(ds - alpha)
						else:
							tmp_poisoned_pl.append(eps_U[j])
					__pls_copy = copy.deepcopy(__pls)
					__dpfsys_copy = copy.deepcopy(__dpfsys)

					## Create Branch
					__pls_copy.insert(ts, tmp_poisoned_pl)
					assert(__dpfsys_copy.timestamp == ts)
					__dpfsys_copy.AddToWaiting(tmp_poisoned_pl)
					__dpfsys_copy.OnPipelineArrival(tmp_poisoned_pl)
					complete = __dpfsys_copy.OnSchedulerTimer()
					if ts not in complete:
						print(ts, __dpfsys_copy.timestamp, complete)
						print(__dpfsys.eps_U)
						print(eps_U)
						print(__dpfsys_copy.eps_U)
						print(__dpfsys_copy.wp)
					assert(ts in complete)
					__pls_tmp, branch_max_sum = __DFS_depth_limited(__pls_copy, __dpfsys_copy, ts+1, depth-1)
					branch_max_sum += sum(tmp_poisoned_pl)
					if branch_max_sum > max_branch:
						max_branch = branch_max_sum
						max_pls = __pls_tmp

					## Do Fake Allocation
					for j in range(M):
						assert(eps_U[j] >= pl[j])
						eps_U[j] -= pl[j]
						if eps_U[j] == 0:
							return max_pls, max_branch

			if True:
				__pls_copy = copy.deepcopy(__pls)
				__dpfsys_copy = copy.deepcopy(__dpfsys)
				## Create Branch
				tmp_poisoned_pl = copy.deepcopy(eps_U)
				__pls_copy.insert(ts, tmp_poisoned_pl)
				__dpfsys_copy.AddToWaiting(tmp_poisoned_pl)
				__dpfsys_copy.OnPipelineArrival(tmp_poisoned_pl)
				complete = __dpfsys_copy.OnSchedulerTimer()
				if ts not in complete:
					print(ts, complete)
					print(__dpfsys.eps_U)
					print(eps_U)
					print(__dpfsys_copy.eps_U)
					print(__dpfsys_copy.wp)
				assert(ts in complete)
				__pls_tmp, branch_max_sum = __DFS_depth_limited(__pls_copy, __dpfsys_copy, ts+1, depth-1)
				branch_max_sum += sum(tmp_poisoned_pl)
				if branch_max_sum > max_branch:
					max_branch = branch_max_sum
					max_pls = __pls_tmp

			return max_pls, max_branch

		__sum = dec(0)
		while len(__poisoned_list) > 0:
			__dpfsys = dpf.DPF(eps_Global, N, M)
			__pls, __sum_depth = __DFS_depth_limited(__pls, __dpfsys, 0, __d)
			__poisoned_list = __poisoned_list[__d:]
			__sum += __sum_depth

		return __pls, __sum

	method_dict = {
		'__Tree_MaxEveryDepth': __Tree_MaxEveryDepth,
		'__Tree_DFS': __Tree_DFS,
		'__Tree_DFS_depth_limited': __Tree_DFS_depth_limited,
	}

	A = method_dict.get(method, __Tree_MaxEveryDepth)

	poisoned_list = []
	k2 = K
	while k2 > 0:
		max_poisoned_list = []
		max_sum = 0

		for ts in range(N-K+1):
			## Append ts to the original poisoned_list
			tmp_poisoned_list = copy.deepcopy(poisoned_list)
			tmp_poisoned_list.append(ts)
			tmp_poisoned_list.sort()
			## Calculate the sum of poisoned pipelines give tmp_poisoned_list
			_, tmp_sum = A(pls, tmp_poisoned_list, **kwargs)
			if tmp_sum > max_sum:
				max_sum = tmp_sum
				max_poisoned_list = tmp_poisoned_list

		poisoned_list = max_poisoned_list
		# print(poisoned_list)
		k2 -= 1

	assert(len(poisoned_list) == K)

	pls, _ = A(pls, poisoned_list, **kwargs)
	for i in range(K):
		poisoned_list[i] += i

	return pls, poisoned_list

def GreedyTheRecalculation(sim_arg: tuple, K: int):
	eps_Global, N, M, pls = sim_arg
	assert(len(pls) + K >= N)

	poisoned_list = []
	k2 = K
	while k2 > 0:
		new_poisoned_list = []
		new_sum = 0
		for insert_ts in range(N-K+1): # no insertion, so it's in the range of N-K+1
			# if insert_ts in poisoned_list:
			# 	continue

			## generate insertion list
			tmp_poisoned_list = copy.deepcopy(poisoned_list)
			tmp_poisoned_list.append(insert_ts)
			tmp_poisoned_list.sort()

			## greedy on each position
			tmp_sum = 0
			dpfsys = dpf.DPF(eps_Global, N, M)
			for i in range(N-K+1):
				if i in tmp_poisoned_list:
					tmp_poisoned_pl = MaximizeAllocationAtTS(dpfsys)
					tmp_sum += sum(tmp_poisoned_pl)
					dpfsys.AddToWaiting(tmp_poisoned_pl)
					dpfsys.OnPipelineArrival(tmp_poisoned_pl)
					dpfsys.OnSchedulerTimer()
				if i >= N-K:
					break
				dpfsys.AddToWaiting(pls[i])
				dpfsys.OnPipelineArrival(pls[i])
				dpfsys.OnSchedulerTimer()

			if tmp_sum > new_sum:
				new_sum = tmp_sum
				new_poisoned_list = tmp_poisoned_list

		## len(poisoned_list) += 1
		poisoned_list = new_poisoned_list
		# print(poisoned_list)
		k2 -= 1

	assert(len(poisoned_list) == K)
	k1 = 0
	for i in range(K):
		poisoned_list[i] += k1
		k1 += 1

	k1 = 0
	k2 = K
	dpfsys = dpf.DPF(eps_Global, N, M)
	for i in range(N):
		if i in poisoned_list:
			poisoned_pl = MaximizeAllocationAtTS(dpfsys)
			pls.insert(i, poisoned_pl)
		dpfsys.AddToWaiting(pls[i])
		dpfsys.OnPipelineArrival(pls[i])
		finished_pls_seq = dpfsys.OnSchedulerTimer()
		if i in poisoned_list:
			assert(i in finished_pls_seq)

	return pls, poisoned_list

def BlockGreedy(sim_arg: tuple, K: int):
	eps_Global, N, M, pls = sim_arg
	assert(len(pls) + K >= N)

	ds_id_list = getDominantShareIDList(pls)

	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, M=M)
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

def DynamicSequentialAttack_std(sim_arg: tuple, K: int, transzendental: tuple=([], [])):
	eps_Global, N, M, pls = sim_arg
	pre_pls, pre_complete = transzendental
	assert(len(pls) + K >= N)

	ds_id_list = getDominantShareIDList(pls)
	step = dec(dec_format % (eps_Global / N))

	ts = -1
	poisoned_list = []
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, M=M)
	k1 = 0
	k2 = K
	while k2 > 0:
		ts += 1

		unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
		for j in range(M):
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
					ds_i = pl[ds_id_list[seq]]
					if len(pre_pls) > 0:
						for i in pre_complete:
							if i > ts:
								restbudget -= pre_pls[i][j]
					else:
						restbudget -= ds_i * k2
					if restbudget < ds_i:
						return True
					return False
				return __JudgeByDominantShare()

			if AttackAble(seq):
				insert_flag = True
				ds = pl[ds_id_list[seq]]
				break
			else:
				for j in range(M):
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
			for j in range(M):
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

def DynamicSequentialAttack_mod(sim_arg: tuple, K: int):
	eps_Global, N, M, pls = sim_arg
	assert(len(pls) + K >= N)

	ds_id_list = getDominantShareIDList(pls)
	step = dec(dec_format % (eps_Global / N))

	ts = -1
	poisoned_list = []
	dpfsys = dpf.DPF(eps_Global=eps_Global, N=N, M=M)
	k1 = 0
	k2 = K
	while k2 > 0:
		ts += 1

		unallocated_eps_list = copy.deepcopy(dpfsys.eps_U)
		for j in range(M):
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
				ds_id = ds_id_list[seq]
				assert(pl != None)
				return ((N-ts-k2)/k2) < pl[ds_id]

			if AttackAble(seq):
				insert_flag = True
				ds = pl[ds_id_list[seq]]
				break
			else:
				for j in range(M):
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
			for j in range(M):
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

## Run Functions
def main_gen(config: dict, verbose=False) -> list:
	N = config.get('N', 100)
	M = config.get('M', 10)
	K = config.get('K', 10)
	step = config.get('step', 1.0)
	sigma_mice = config.get('sigma_mice', 10.0) # Expectation is 0.1
	sigma_elephant = config.get('sigma_elephant', 1.0) # Expectation is 1.0
	ratio = config.get('ratio', 0.75) # mice ratio

	eps_Global = N * step
	# benign_pls = GenDataset(ratio, N, M, sigma_mice=sigma_mice, sigma_elephant=sigma_elephant)
	benign_pls = ReadDataset(N)
	sim_arg = (eps_Global, N, M, benign_pls)
	if verbose:
		PrintPipelines(benign_pls, N)

	def CallFunc(funcname, **kwargs) -> float:
		start_time = time.time()
		pls, poisoned_list = funcname(copy.deepcopy(sim_arg), K, **kwargs)
		duration = time.time() - start_time
		sim_arg1 = (eps_Global, N, M, pls)
		complete = dpf.Simulation(sim_arg1)
		complete_poisoned = []
		for i in poisoned_list:
			if i in complete:
				complete_poisoned.append(i)
		perc = float(SumPipelines(pls, complete_poisoned)) / (N * M * step)
		if not verbose:
			print(ReturnFunctionName(funcname), kwargs)
			print('%.4f' % perc, '%.4f' % duration, poisoned_list)
		if verbose:
			print(ReturnFunctionName(funcname))
			print('%4f' % perc)
			print('%4f' % duration)
			print(poisoned_list)
			PrintPipelines(pls, N)
		return float(perc)

	return [
		# CallFunc(GreedyTheRecalculation),
		# CallFunc(RandomAttack),
		# CallFunc(NaiveGreedy),
		# CallFunc(BlockGreedy),
		# CallFunc(DynamicSequentialAttack_std),
		# CallFunc(DynamicSequentialAttack_mod),
		CallFunc(GreedyFramework, method='__Tree_MaxEveryDepth'),
		# CallFunc(GreedyFramework, method='__Tree_DFS_depth_limited', __d=1),
		# CallFunc(GreedyFramework, method='__Tree_DFS_depth_limited', __d=2),
		# CallFunc(GreedyFramework, method='__Tree_DFS_depth_limited', __d=4),
		# CallFunc(GreedyFramework, method='__Tree_DFS_depth_limited', __d=K),
	]

def main_onerun():
	N = int(input())
	M = int(input())
	K = int(input())
	step = float(input())
	config = {
		'N': N,
		'M': M,
		'K': K,
		'step': step,
	}
	main_gen(config, verbose=True)

if __name__ == '__main__':
	# main_gen(bpn=100, Kperc=0.05, verbose=True)
	main_onerun()
