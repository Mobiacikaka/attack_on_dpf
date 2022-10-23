#!/usr/bin/python3
# vim:ts=2:sw=2:noet
from decimal import Decimal as dec
import random
import dpf
import copy
import statistics

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

def gendata(eps_Global, N, NPB, sigma=1.0) -> tuple:
	benign_pls	= []
	for _ in range(int(N * 1.1)):
		pl = []
		for _ in range(NPB):
			rnd = random.expovariate(sigma)
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
	for item in pl:
		print(float(item), end='\t')
	print()

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

def GreedyTheRecalculation(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) + K >= N)

	poisoned_list = []
	k1 = 0
	k2 = K
	while k2 > 0:
		new_poisoned_list = []
		new_sum = 0
		for insert_ts in range(N-K+1):
			if insert_ts in poisoned_list:
				continue

			## generate insertion list
			tmp_poisoned_list = copy.deepcopy(poisoned_list)
			tmp_poisoned_list.append(insert_ts)
			tmp_poisoned_list.sort()

			## greedy on each position
			tmp_sum = 0
			dpfsys = dpf.DPF(eps_Global, N, NPB)
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
		k1 += 1
		k2 -= 1

	assert(len(poisoned_list) == K)
	k1 = 0
	for i in range(K):
		poisoned_list[i] += k1
		k1 += 1

	k1 = 0
	k2 = K
	dpfsys = dpf.DPF(eps_Global, N, NPB)
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
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) + K >= N)

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

def DynamicSequentialAttack_std(sim_arg: tuple, K: int, transzendental: tuple[list, list]=([], [])):
	eps_Global, N, NPB, pls = sim_arg
	pre_pls, pre_complete = transzendental
	assert(len(pls) + K >= N)

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

def DynamicSequentialAttack_mod(sim_arg: tuple, K: int):
	eps_Global, N, NPB, pls = sim_arg
	assert(len(pls) + K >= N)

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
			print("failed", pls[ts])
			print("spare", dpfsys.eps_U)
			assert(0)

	return pls, poisoned_list

## Run Functions
def main_gen(N, M, K, step=1.0, sigma=1.0, verbose=False) -> list:
	eps_Global, N, NPB, benign_pls = gendata(N* step, N, M, sigma=sigma)
	# eps_Global, N, NPB, benign_pls = readdata('data.csv')
	sim_arg = (eps_Global, N, NPB, benign_pls)
	if verbose:
		PrintPipelines(benign_pls, N)

	def CallFunc(funcname) -> float:
		pls, poisoned_list = funcname(copy.deepcopy(sim_arg), K)
		sim_arg1 = (eps_Global, N, NPB, pls)
		complete = dpf.Simulation(sim_arg1)
		for i in poisoned_list:
			assert(i in complete)
		perc = SumPipelines(pls, poisoned_list) / (N * NPB)
		if verbose:
			print(str(funcname))
			print(poisoned_list)
			print('%.4f' % perc)
			PrintPipelines(pls)
		return float(perc)

	return [
		CallFunc(GreedyTheRecalculation),
		CallFunc(BlockGreedy),
		CallFunc(DynamicSequentialAttack_std),
		CallFunc(DynamicSequentialAttack_mod),
	]

def main_onerun():
	sigma = float(input())
	N = int(input())
	M = int(input())
	K = int(input())
	step = float(input())
	main_gen(N, M, K, step, sigma=sigma, verbose=True)

def main_multirun(times=100):
	perclist = []
	for time in range(times):
		# if time % 10 == 0:
		# 	print(time)
		N = 40
		perc = main_gen(N=N, M=10, K=int(N * 0.2), verbose=True)
		for i in range(len(perc)):
			if i >= len(perclist):
				perclist.append([])
			perclist[i].append(perc[i])
	for i in range(len(perclist)):
		print("%.4f"%statistics.mean(perclist[i]))

if __name__ == '__main__':
	# main_gen(bpn=100, Kperc=0.05, verbose=True)
	# main_multirun(times=1)
	main_onerun()
