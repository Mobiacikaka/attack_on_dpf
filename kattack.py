#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import random
import dpf
import copy
import chooseK as ck

alpha = 0.01
k = 3

def return_eps_U_list(sim_arg: tuple) -> list[list[float]]:
	eps_Global, first_NPL, NPB, benign_pls = sim_arg
	dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
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
	eps_Global, first_NPL, NPB, benign_pls = sim_arg

	dpfsys = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
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
	first_NPL		= 10
	NPB					= 10
	benign_pls	= []
	for _ in range(first_NPL * 3):
		step = eps_Global / first_NPL
		pl = [random.uniform(step * 0.5, step * 1.15) for _ in range(NPB)]
		benign_pls.append(pl)

	return eps_Global, first_NPL, NPB, benign_pls

def func3():
	eps_Global, first_NPL, NPB, benign_pls = gendata()

	pls = benign_pls
	sim_arg = eps_Global, first_NPL, NPB, pls
	eps_U_list = return_eps_U_list(sim_arg)
	rklist = ck.brute_force(eps_U_list, first_NPL, NPB, k)
	for pl in pls[:first_NPL]:
		print(["%.2f"%item for item in pl])
	print()
	for ulist in eps_U_list[:first_NPL]:
		print(["%.2f"%item for item in ulist])
	print()
	print(ck.compress_rowlist(rklist, eps_U_list))
	print()

	pls = benign_pls[:first_NPL-k] + [[alpha] * NPB] * k + benign_pls[first_NPL-k:]
	sim_arg = eps_Global, first_NPL, NPB, pls
	eps_U_list = return_eps_U_list(sim_arg)
	rklist = ck.brute_force(eps_U_list, first_NPL, NPB, k)
	for pl in pls[:first_NPL]:
		print(["%.2f"%item for item in pl])
	print()
	for ulist in eps_U_list[:first_NPL]:
		print(["%.2f"%item for item in ulist])
	print()
	print(ck.compress_rowlist(rklist, eps_U_list))

def func2():
	eps_Global, first_NPL, NPB, benign_pls = gendata()

	# pls = benign_pls[:first_NPL-k] + [ [alpha] * NPB ] * k + benign_pls[first_NPL-k:]
	pls = benign_pls
	sim_arg = eps_Global, first_NPL, NPB, pls
	eps_U_list = return_eps_U_list(sim_arg)
	for pl in pls[:first_NPL]:
		print(["%.2f"%item for item in pl])
	print()
	for ulist in eps_U_list[:first_NPL]:
		print(["%.2f"%item for item in ulist])
	print()

	def single_attack(pls, ulist):
		maxv = 0
		maxx = 0
		maxy = 0
		for i in range(len(ulist) - k+1):
			for j in range(len(ulist[i])):
				if ulist[i][j] > maxv:
					maxv = ulist[i][j]
					maxx = i
					maxy = j
		pl = []
		for _ in range(maxy):
			pl.append(0)
		pl.append(maxv + 1.0)
		for _ in range(10-maxy-1):
			pl.append(0)
		assert(len(pl) == 10)
		pls.insert(maxx, pl)
		return pls
	
	pls = single_attack(benign_pls, eps_U_list[:first_NPL])
	# for _ in range(k-1):
	# 	pls.insert(first_NPL - k + 1, [ alpha ] * NPB)
	sim_arg = eps_Global, first_NPL, NPB, pls
	eps_U_list = return_eps_U_list(sim_arg)
	for pl in pls[:first_NPL+1]:
		print(["%.2f"%item for item in pl])
	print()
	for ulist in eps_U_list[:first_NPL+1]:
		print(["%.2f"%item for item in ulist])

def func1():
	eps_Global, first_NPL, NPB, benign_pls = gendata()
	sim_arg = eps_Global, first_NPL, NPB, benign_pls
	finish_num = len(dpf.Simulation(sim_arg))
	print("finish_num: ", finish_num)

	pls, poison_pls_no = brute_force_with_kinsert(sim_arg, 3)
	sim_arg = eps_Global, first_NPL, NPB, benign_pls
	finish_pls_no = dpf.Simulation(sim_arg)
	finish_num = len(finish_pls_no)
	for item in poison_pls_no:
		if item in finish_pls_no:
			finish_num -= 1
	print("finish_num: ", finish_num)
