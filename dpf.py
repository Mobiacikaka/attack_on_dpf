#!/bin/python3
# vim:ts=2:sw=2:noet
from typing import Sequence
from functools import cmp_to_key

class Pipelines:

	def __init__(self, sequence: int):
		self.seq = sequence
		self.demand = []

	def append(self, demand: float):
		self.demand.append(demand)

class DPF:

	def __init__(self, eps_Global: float=5.0, first_NPL=5):
		self.eps_Global = eps_Global
		self.NPB = 0	# number of privacy block
		self.first_NPL = first_NPL # first N pipelines
		self.eps_G = [] # global budget
		self.eps_U = [] # unlocked budget
		self.eps_A = [] # allocated budget
		self.eps_C = [] # consume budget

	def OnDataBlockCreation(self, j: int) -> None:
		assert(len(self.eps_G) == j)
		self.eps_G.append(self.eps_Global)
		self.eps_U.append(0)
		self.eps_A.append(0)
		self.eps_C.append(0)
		self.NPB += 1

	def OnPipelineArrival(self, pl: Pipelines) -> None:
		d_i = pl.demand
		for j in range(self.NPB):
			if d_i[j] > 0:
				self.eps_U[j] = min(self.eps_G[j] - self.eps_C[j], self.eps_U[j] + self.eps_G[j] / self.first_NPL)

	def cmp_DominantShare(self, pl1: Pipelines, pl2: Pipelines):
		ds1 = self.DominantShare(pl1.demand)
		ds2 = self.DominantShare(pl2.demand)
		if ds1 < ds2:
			return -1
		elif ds1 > ds2:
			return 1
		else:
			return 0

	def OnSchedulerTimer(self, wp: list[Pipelines]) -> None:
		sorted_pipelines = sorted(wp, key=cmp_to_key(self.cmp_DominantShare))
		i = 0
		pop_list = []
		while i < len(sorted_pipelines):
			d_i = sorted_pipelines[i].demand
			if(self.CanRun(d_i)):
				self.Allocate(d_i)
				# Run task i
				task_complete_flag = True
				if task_complete_flag == True:
					for j in range(self.NPB):
						self.eps_C[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
					seq = sorted_pipelines[i].seq
					pop_list.append(seq)
					sorted_pipelines.pop(i)
					i -= 1
				else:
					for j in range(self.NPB):
						self.eps_U[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
			i += 1
		for item in wp:
			if item.seq in pop_list:
				wp.remove(item)

	def DominantShare(self, d_i: Sequence[float]) -> float:
		max_share = 0
		for j in range(self.NPB):
			if d_i[j] > 0:
				share = d_i[j] / self.eps_G[j]
				if share > max_share:
					max_share = share
		return max_share

	def CanRun(self, d_i: Sequence[float]) -> bool:
		flag = True
		for j in range(self.NPB):
			if d_i[j] > self.eps_U[j]:
				flag = False
				break
		return flag

	def Allocate(self, d_i: Sequence[float]) -> None:
		for j in range(self.NPB):
			self.eps_U[j] -= d_i[j]
			self.eps_A[j] += d_i[j]

def Simulation():
	eps_Global = float(input())
	first_NPL	 = int(input())
	dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)

	NPB = int(input())
	for j in range(NPB):
		dpf.OnDataBlockCreation(j)

	NPL = int(input())
	wp = []
	for i in range(NPL):
		pl = Pipelines(i)
		line = input()
		pl.demand = [float(item) for item in line.split()]
		dpf.OnPipelineArrival(pl)
		wp.append(pl)
		dpf.OnSchedulerTimer(wp)

	for pl in wp:
		print(pl.seq, end=" ")
	print()

Simulation()
