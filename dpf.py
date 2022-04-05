#!/bin/python3
# vim:ts=2:sw=2:noet
from typing import Sequence
from functools import cmp_to_key

class DPF:

	def __init__(self, eps_Global: float=5.0, first_NPL=5):
		self.eps_Global = eps_Global
		self.NPB = 0	# number of privacy block
		self.first_NPL = first_NPL # first N pipelines
		self.eps_G = [] # global budget
		self.eps_U = [] # unlocked budget
		self.eps_A = [] # allocated budget
		self.eps_C = [] # consume budget
		self.finish_pls_no = []

	def OnDataBlockCreation(self) -> None:
		self.eps_G.append(self.eps_Global)
		self.eps_U.append(0)
		self.eps_A.append(0)
		self.eps_C.append(0)
		self.NPB += 1

	def OnPipelineArrival(self, pl: list[float]) -> None:
		for j in range(self.NPB):
			if pl[j] > 0:
				self.eps_U[j] = min(self.eps_G[j] - self.eps_C[j], self.eps_U[j] + self.eps_G[j] / self.first_NPL)

	# def cmp_DominantShare(self, pl1: list[float], pl2: list[float]):
	def cmp_DominantShare(self, _pl1, _pl2):
		print(type(_pl1))
		pl1 = _pl1.get()
		pl2 = _pl2.get()
		ds1 = self.DominantShare(pl1)
		ds2 = self.DominantShare(pl2)
		if ds1 < ds2:
			return -1
		elif ds1 > ds2:
			return 1
		else:
			return 0

	def OnSchedulerTimer(self, wp: dict[int, list[float]]) -> None:
		sorted_pipelines = sorted(wp, key=lambda x: self.DominantShare(wp.get(x)))
		i = 0
		while i < len(sorted_pipelines):
			seq = sorted_pipelines[i]
			d_i = wp.get(seq)
			assert(d_i != None)
			if(self.CanRun(d_i)):
				self.Allocate(d_i)
				# Run task i
				task_complete_flag = True
				if task_complete_flag == True:
					for j in range(self.NPB):
						self.eps_C[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
					assert(seq not in self.finish_pls_no)
					wp.pop(seq)
					self.finish_pls_no.append(seq)
				else:
					for j in range(self.NPB):
						self.eps_U[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
			i += 1

	def DominantShare(self, d_i) -> float:
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

def Simulation(eps_Global: float, first_NPL: int, NPB: int, pls: list[list[float]]) -> list[int]:
	dpf = DPF(eps_Global=eps_Global, first_NPL=first_NPL)
	for _ in range(NPB):
		dpf.OnDataBlockCreation()
	
	wp = {} # waiting pipelines
	for i in range(len(pls)):
		wp[i] = pls[i]
		dpf.OnPipelineArrival(pls[i])
		dpf.OnSchedulerTimer(wp)

	return dpf.finish_pls_no
