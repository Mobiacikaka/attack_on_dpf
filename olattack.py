#!/bin/python
# vim:ts=2:sw=2:noet

from dpf import DPF
import dpf
from copy import deepcopy
import random

alpha = 0.01

def pre_allocation(wp: dict, dpf: DPF, k: int, index: int, NPB: int) -> tuple[list[list[int|float]], int|float]:
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
	return poison_pls, sum(eps_U)

def olattack_threshold(k: int, sim_arg: tuple) -> tuple:
	eps_Global, first_NPL, NPB, benign_pls = sim_arg
	dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
	for _ in range(NPB):
		dpf.OnDataBlockCreation()
	pls = []
	wp = {}
	i = 0
	index = 0
	threshold = (eps_Global / first_NPL) * NPB * k * 1.1

	# Simulation
	while True:
		## judge if insert
		if first_NPL == index + k:
			# pre-allocation
			poison_pls, _ = pre_allocation(deepcopy(wp), deepcopy(dpf), k, index, NPB)
			pls = benign_pls[:i] + poison_pls + benign_pls[i:]
			break
		else:
			# judge if insert
			poison_pls, tt_alloc = pre_allocation(deepcopy(wp), deepcopy(dpf), k, index, NPB)
			if tt_alloc >= threshold:
				print(tt_alloc, threshold)
				pls = benign_pls[:i] + poison_pls + benign_pls[i:]
				break

		## insert real pipelines
		wp[index] = benign_pls[i]
		dpf.OnPipelineArrival(benign_pls[i])
		dpf.OnSchedulerTimer(wp)
		index += 1
		i += 1
		if i >= len(benign_pls):
			break

	return pls, list(range(index, index+k))

def ensure_alloc_one(wp: dict, dpf: DPF, T_db: float, T_nb: int) -> tuple[bool, list[int|float]]:
	pl1 = []
	nb_max = 0
	flag = False

	if not wp:
		dpf.OnPipelineArrival([1.0] * dpf.NPB)
		for u in dpf.eps_U:
			if u > T_db:
				pl1.append(u)
				nb_max += 1
			else:
				pl1.append(alpha)
		if nb_max >= T_nb:
			flag = True
	else:
		sorted_pipelines = sorted(wp, key=lambda x: dpf.DominantShareList(wp.get(x)))
		dpf.OnPipelineArrival([1.0] * dpf.NPB)
		for item in sorted_pipelines:
			demand_i = wp.get(item)
			assert(demand_i != None)
			nb_tmp = 0
			pl2 = []

			if dpf.CanRun(demand_i):
				maxdemand = max(demand_i) - alpha
				for u in dpf.eps_U:
					if u >= T_db:
						pl2.append(u if u <= maxdemand else maxdemand)
						nb_tmp += 1
					else:
						pl2.append(alpha)
			else:
				for u in dpf.eps_U:
					if u >= T_db:
						pl2.append(u)
						nb_tmp += 1
					else:
						pl2.append(alpha)

			if nb_tmp >= T_nb:
				# if sum(pl2) > sum(pl1)
				if nb_tmp < nb_max:
					continue
				elif nb_tmp == nb_max:
					if sum(pl2) <= sum(pl1):
						continue
				pl1 = pl2
				nb_max = nb_tmp

	return flag, pl1

def olattack_1inarow(k: int, sim_arg) -> tuple:
	eps_Global, first_NPL, NPB, benign_pls = sim_arg
	dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
	for _ in range(NPB):
		dpf.OnDataBlockCreation()
	pls = []
	poison_pls_no = []
	wp = {}
	i = 0
	index = 0
	T_db = 1.5 * eps_Global / first_NPL
	T_nb = int(NPB / k)

	# Simulation
	for i in range(len(benign_pls)):
		if k <= 0:
			pass
		elif first_NPL == index + k:
			poison_pls, _ = pre_allocation(deepcopy(wp), deepcopy(dpf), k, index, NPB)
			for poison_pl in poison_pls:
				poison_pls_no.append(index)
				pls.append(poison_pl)
				wp[index] = poison_pl
				index += 1
				dpf.OnPipelineArrival(poison_pl)
				dpf.OnSchedulerTimer(wp)
		else:
			flag, poison_pl = ensure_alloc_one(wp=deepcopy(wp), dpf=deepcopy(dpf), T_db=T_db, T_nb=T_nb)
			if flag:
				print(k, ["%.2f"%item for item in poison_pl])
				pls.append(poison_pl)
				wp[index] = poison_pl
				poison_pls_no.append(index)
				index += 1
				k -= 1
				dpf.OnPipelineArrival(poison_pl)
				dpf.OnSchedulerTimer(wp)

		pls.append(benign_pls[i])
		wp[index] = benign_pls[i]
		index += 1
		dpf.OnPipelineArrival(benign_pls[i])
		dpf.OnSchedulerTimer(wp)

	return pls, poison_pls_no

def gendata() -> tuple:
	eps_Global	= 10.0
	first_NPL		= 10
	NPB					= 10
	benign_pls	= []
	for _ in range(first_NPL * 2):
		step = eps_Global / first_NPL
		pl = [random.uniform(step * 0.5, step * 1.1) for _ in range(NPB)]
		# print(["%.2f"%item for item in pl])
		benign_pls.append(pl)

	return eps_Global, first_NPL, NPB, benign_pls

if __name__ == '__main__':
	sim_arg = gendata()
	pls, poison_pls_no = olattack_1inarow(3, sim_arg)
	print("poison_pls_no", poison_pls_no)
	for no in poison_pls_no:
		print(["%.2f"%item for item in pls[no]])
	finish_pls_no = dpf.Simulation(sim_arg)
	for item in poison_pls_no:
		if item not in finish_pls_no:
			print(item, " not finish")
			assert(0)
