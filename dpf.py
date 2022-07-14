#!/bin/python3
# vim:ts=2:sw=2:noet
from typing import Sequence

class DPF:
	def __init__(self, eps_Global: float=5.0, N=5):
		self.eps_Global = eps_Global
		self.NPB = 0	# number of privacy block
		self.N = N # first N pipelines
		self.eps_G = [] # global budget
		self.eps_U = [] # unlocked budget
		self.eps_A = [] # allocated budget
		self.eps_C = [] # consume budget
		self.finish_pls_no = []
		self.finish_sum = []

	def OnDataBlockCreation(self) -> None:
		self.eps_G.append(self.eps_Global)
		self.eps_U.append(0)
		self.eps_A.append(0)
		self.eps_C.append(0)
		self.finish_sum.append(0)
		self.NPB += 1

	def OnPipelineArrival(self, pl: list[int|float]) -> None:
		for j in range(self.NPB):
			if pl[j] > 0:
				self.eps_U[j] = min(self.eps_G[j] - self.eps_C[j], self.eps_U[j] + self.eps_G[j] / self.N)

	def OnSchedulerTimer(self, wp: dict[int, list[float]]) -> list[int]:
		sorted_pipelines = sorted(wp, key=lambda x: self.DominantShareList(wp.get(x)))
		i = 0
		finished = []
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
					finished.append(seq)
					self.finish_sum = [self.finish_sum[l]+d_i[l] for l in range(self.NPB)]
				else:
					for j in range(self.NPB):
						self.eps_U[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
			i += 1
		return finished

	def DominantShare(self, d_i) -> float:
		max_share = 0
		for j in range(self.NPB):
			if d_i[j] > 0:
				share = d_i[j] / self.eps_G[j]
				if share > max_share:
					max_share = share
		return max_share

	def DominantShareList(self, d_i) -> list[float]:
		ds = []
		for j in range(self.NPB):
			ds.append(d_i[j] / self.eps_G[j])
		ds.sort(reverse=True)
		return ds

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

def Simulation(sim_arg: tuple) -> list[int]:
	eps_Global, N, NPB, pls = sim_arg
	dpf = DPF(eps_Global=eps_Global, N=N)
	for _ in range(NPB):
		dpf.OnDataBlockCreation()
	
	wp = {} # waiting pipelines
	for i in range(len(pls)):
		wp[i] = pls[i]
		dpf.OnPipelineArrival(pls[i])
		print(dpf.OnSchedulerTimer(wp))

	print("finish_sum", ["%.2f"%item for item in dpf.finish_sum])
	return dpf.finish_pls_no
