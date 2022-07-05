#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
from copy import deepcopy
import random

def online_attack(k: int, sim_arg: tuple) -> tuple:
	def Simulation():
		nonlocal k, sim_arg
		eps_Global, first_NPL, NPB, benign_pls = sim_arg
		dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
		for _ in range(NPB):
			dpf.OnDataBlockCreation()
		pls = []

		wp = {}
		i = 0
		index = 0
		threshold = (eps_Global / first_NPL) * NPB * k * 1.1
		while True:
			## judge if insert
			print("shit")
			def pre_allocation(wp: dict, dpf: DPF, k: int, index: int, NPB: int) -> tuple[list[list[int|float]], int|float]:
				alpha = 0.01
				for _ in range(k):
					wp[index] = [alpha] * NPB
					dpf.OnPipelineArrival([alpha] * NPB)
					dpf.OnSchedulerTimer(wp)
					index += 1
				eps_U = dpf.eps_U
				poison_pls = []
				for _ in range(k-1):
					poison_pls.append([alpha] * NPB)
				poison_pls.append(eps_U)
				print(["%.2f"%item for item in eps_U])
				return poison_pls, sum(eps_U)

			if first_NPL == index + k:
				# pre-allocation
				poison_pls, _ = pre_allocation(deepcopy(wp), deepcopy(dpf), k, index, NPB)
				pls = benign_pls[:i] + poison_pls + benign_pls[i:]
				break
			else:
				# judge if insert
				poison_pls, tt_alloc = pre_allocation(deepcopy(wp), deepcopy(dpf), k, index, NPB)
				if tt_alloc >= threshold:
					pls = benign_pls[:i] + poison_pls + benign_pls[i:]
					break

			## insert benign pipelines
			wp[index] = benign_pls[i]
			dpf.OnPipelineArrival(benign_pls[i])
			dpf.OnSchedulerTimer(wp)
			index += 1
			i += 1
			if i >= len(benign_pls):
				break

		return pls, list(range(index, index+k))

	return Simulation()

def gendata() -> tuple:
	eps_Global	= 50.0
	first_NPL		= 10
	NPB					= 10
	benign_pls	= []
	for _ in range(first_NPL * 2):
		step = eps_Global / first_NPL
		pl = [random.uniform(step * 0.5, step * 1.25) for _ in range(NPB)]
		print(["%.2f"%item for item in pl])
		benign_pls.append(pl)

	return eps_Global, first_NPL, NPB, benign_pls

if __name__ == '__main__':
	# eps_Global = float(input())
	# first_NPL = int(input())
	# NPB = int(input()) # number of data block

	# NPL = int(input())
	# benign_pls = []
	# for _ in range(NPL):
	# 	benign_pls.append([float(i) for i in input().split()])

	sim_arg = gendata()
	pls, poison_pls_no = online_attack(5, sim_arg)
