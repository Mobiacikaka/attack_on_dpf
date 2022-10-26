#!/usr/bin/python3
# vim:ts=2:sw=2:noet
from decimal import Decimal as dec

dec_format = '%.2f'

class DPF:
	def __init__(self, eps_Global: float, N: int, NPB: int):
		self.eps_Global = dec(str(dec_format % eps_Global))
		self.NPB = NPB	# number of privacy block
		self.N = N # first N pipelines
		self.eps_G = [] # global budget
		self.eps_U = [] # unlocked budget
		self.eps_A = [] # allocated budget
		self.eps_C = [] # consume budget
		self.complete_pl_list = []
		self.wp = {} # waiting pipelines
		self.timestamp = 0
		for _ in range(NPB):
			self.OnDataBlockCreation()

	def OnDataBlockCreation(self) -> None:
		self.eps_G.append(self.eps_Global)
		self.eps_U.append(dec(dec_format % 0))
		self.eps_A.append(dec(dec_format % 0))
		self.eps_C.append(dec(dec_format % 0))

	def AddToWaiting(self, pl: list):
		self.wp[self.timestamp] = pl
		self.timestamp += 1

	def OnPipelineArrival(self, pl: list) -> None:
		for j in range(self.NPB):
			if pl[j] > 0:
				self.eps_U[j] = min(self.eps_G[j] - self.eps_C[j], self.eps_U[j] + self.eps_G[j] / self.N)

	def SortWaitingPipelines(self):
		return sorted(self.wp, key=lambda x: self.DominantShareList(self.wp.get(x)))

	def OnSchedulerTimer(self) -> list:
		sorted_pipelines = self.SortWaitingPipelines()
		i = 0
		finished = []
		while i < len(sorted_pipelines):
			seq = sorted_pipelines[i]
			d_i = self.wp.get(seq)
			assert(d_i != None)
			if(self.CanRun(d_i)):
				self.Allocate(d_i)
				# Run task i
				task_complete_flag = True
				if task_complete_flag == True:
					for j in range(self.NPB):
						self.eps_C[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
					assert(seq not in self.complete_pl_list)
					self.wp.pop(seq)
					self.complete_pl_list.append(seq)
					finished.append(seq)
				else:
					for j in range(self.NPB):
						self.eps_U[j] += d_i[j]
						self.eps_A[j] -= d_i[j]
			i += 1
		return finished

	def DominantShare(self, d_i) -> dec:
		max_share = dec(dec_format % 0)
		for j in range(self.NPB):
			if d_i[j] > 0:
				share = d_i[j] / self.eps_G[j]
				if share > max_share:
					max_share = share
		return max_share

	def DominantShareList(self, d_i) -> list:
		ds = []
		for j in range(self.NPB):
			ds.append(d_i[j] / self.eps_G[j])
		ds.sort(reverse=True)
		return ds

	def CanRun(self, d_i: list, unallocated_eps_list: list=[]) -> bool:
		if len(unallocated_eps_list) == 0:
			unallocated_eps_list = self.eps_U
		assert(len(d_i) == len(unallocated_eps_list))

		for j in range(self.NPB):
			if d_i[j] > unallocated_eps_list[j]:
				return False
		return True

	def Allocate(self, d_i: list) -> None:
		for j in range(self.NPB):
			self.eps_U[j] -= d_i[j]
			self.eps_A[j] += d_i[j]

	## Remove completed pipeline from completed list
	def deComplete(self, d_i: list, seq) -> None:
		for j in range(self.NPB):
			self.eps_U[j] += d_i[j]
			self.eps_C[j] -= d_i[j]
		self.complete_pl_list.remove(seq)
		self.wp[seq] = d_i

def Simulation(sim_arg: tuple, verbose: bool=False) -> list:
	eps_Global, N, NPB, pls = sim_arg
	dpf = DPF(eps_Global=eps_Global, N=N, NPB=NPB)

	for pl in pls:
		pre_Allocation_one(dpf, pl, verbose)

	if verbose:
		print("finish_sum", [dec_format % item for item in dpf.eps_C])
	return dpf.complete_pl_list

def pre_Allocation_one(dpf: DPF, pl, verbose: bool=False):
	dpf.AddToWaiting(pl)
	dpf.OnPipelineArrival(pl)
	finished_pls = dpf.OnSchedulerTimer()
	if verbose:
		print(f"{dpf.timestamp-1}  ", [dec_format % u for u in dpf.eps_U])
		print(f"{dpf.timestamp-1}  ", finished_pls)
	return dpf, finished_pls
