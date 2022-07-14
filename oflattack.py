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

def atkable(sim_arg, ds_id_list) -> list[bool]:
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

def allocation(sim_arg, k, rklist):
	eps_Global, N, NPB, pls = sim_arg

	# rklist should be sorted
	rklist.sort()
	for rid in rklist:
		pls.insert(rid, [alpha] * NPB)

	dpfsys = DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpfsys.OnDataBlockCreation()

	wp = {}
	index = 0
	while index < rklist[0]:
		wp[index] = pls[index]
		dpfsys.OnPipelineArrival(pls[index])
		dpfsys.OnSchedulerTimer(wp)
		index += 1
	
	def pre_allocation_one(dpfsys, wp, index) -> list:
		wp[index] = pls[index]
		dpfsys.OnPipelineArrival(pls[index])
		return dpfsys.OnSchedulerTimer(wp)

	ds_id_list = gen_dominantshare_block_id_list(pls, N, NPB)
	atkable_list = atkable(sim_arg, ds_id_list)
	print(ds_id_list)
	print(atkable_list)

	robbery_list = []
	blocking_list = []

	def func_A(rklist_no):
		assert(index == rklist[rklist_no])
		print(rklist[rklist_no])
		_dpfsys = copy.deepcopy(dpfsys)
		_wp = copy.deepcopy(wp)
		cur_poisoned_pl_no = rklist[rklist_no]
		nxt_poisoned_pl_no = rklist[rklist_no+1]

		robbery = {}
		blocking = {}

		# add basic robbery and blocking pl to dict
		for i in range(N):
			if atkable_list[i] == True and i not in dpfsys.finish_pls_no:
				if i > cur_poisoned_pl_no:
					blocking[i] = 0

		# calculate MIN value for blocking
		# calculate MAX value for robbery
		for i in range(cur_poisoned_pl_no, nxt_poisoned_pl_no):
			_wp[i] = pls[i]
			_dpfsys.OnPipelineArrival(pls[i])
			finished = _dpfsys.OnSchedulerTimer(_wp)
			print(finished)
			for pl in finished:
				if atkable_list[pl] == True:
					ds_id = ds_id_list[pl]
					if pl < cur_poisoned_pl_no:
						robbery[pl] = pls[pl][ds_id]
					else:
						blocking[pl] = dpfsys.eps_U[ds_id] + 2 * eps_Global/N - pls[pl][ds_id]

		# clear unattackable robbery pipeline
		while True:
			min_robbery_key = min(robbery, key=robbery.get)
			min_robbery_val = robbery.get(min_robbery_key)
			flag = True
			for key, value in blocking.items():
				if value >= min_robbery_val:
					flag = False
			if flag == False:
				robbery.pop(min_robbery_key)
				atkable_list[min_robbery_key] = False
			else:
				break

		print(robbery)
		print(blocking)
		robbery_list.append(robbery)
		blocking_list.append(blocking)
	
	for rklist_no in rklist:
		if rklist_no != N-1:
			func_A(rklist_no)
		else:
			func_B(rklist_no)

if __name__ == '__main__':
	eps_Global, N, NPB, benign_pls = readdata()

	pls = benign_pls
	sim_arg = eps_Global, N, NPB, pls
	rklist = list(range(N-2*k+1, N, 2))
	allocation(sim_arg, k, rklist)
	# eps_U_list = return_eps_U_list(sim_arg)
	# finish_num = len(dpf.Simulation(sim_arg))
	# for i in range(N):
	# 	print(['%.2f'%item for item in pls[i]])
	# print()
	# for i in range(N):
	# 	print(['%.2f'%item for item in eps_U_list[i]])
	# print("finish_num: ", finish_num)
