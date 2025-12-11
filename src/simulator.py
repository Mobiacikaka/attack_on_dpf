import random
from scheduler.dpf import DPFScheduler
from scheduler.pipeline import Pipeline
from attacker.attacker import BasicAttacker

import numpy

class Simulator:
	def __init__(
		self,
		GlobalEpsilon: int,
		NumberFirstPL: int,
		NumBlock: int,
		PipelineList: list,
		NumAtkPL: int,
		verbose: bool=True,
	) -> None:
		self.GlobalEpsilon: int = GlobalEpsilon
		self.NumberFirstPL: int = NumberFirstPL
		self.NumBlock: int = NumBlock
		self.PipelineList: list[Pipeline] = PipelineList
		self.NumAtkPL: int = NumAtkPL
		self.verbose: bool = verbose
		self.AttackerClass: type[BasicAttacker] = BasicAttacker

	def SetAttacker(self, attacker: BasicAttacker) -> None:
		self.attacker = attacker

	def GeneratePipelineList(
		self,
		mice_ratio=0,
		elephant_ratio=100,
		mice_scale=10,
		elephant_scale=100,
	) -> None:
		"""
		Generate Synthetic Pipeline
			using exponential distribution
		"""
		assert(mice_ratio + elephant_ratio == 100)
		assert(mice_scale < elephant_scale)

		if self.verbose == True:
			print("\n---- Generate Synthetic Pipeline List ----")
			print("mice_ratio:\t", mice_ratio)
			print("elephant_ratio:\t", elephant_ratio)
			print("mice_scale:\t", mice_scale)
			print("elephant_scale:\t", elephant_scale)

		## Ensure there are at least a portion of elephant pipeline
		## abandon the former method which will lead to zero elephant pipelines
		mice_num: int = int(
			numpy.ceil(
				self.NumberFirstPL * mice_ratio / (mice_ratio + elephant_ratio)
			)
		)
		elephant_num: int = int(
			numpy.ceil(
				self.NumberFirstPL * elephant_ratio / (mice_ratio + elephant_ratio)
			)
		)
		PipelineAttrList: list = ['mice'] * mice_num + ['elephant'] * elephant_num
		numpy.random.shuffle(PipelineAttrList)

		PipelineList: list[Pipeline] = []
		for index in range(self.NumberFirstPL):
			## 确定该Pipeline是mice还是elephant
			scale: int = 0
			if PipelineAttrList[index] == 'mice':
				scale = mice_scale
			elif PipelineAttrList[index] == 'elephant':
				scale = elephant_scale

			## 生成Demand，由于demand不能为0，因此要在去掉尾数后加1，所以在生成随机数时要预先给期望减1
			DemandList: list = numpy.random.exponential(scale=scale-1, size=self.NumBlock).tolist()
			DemandList = [int(x) + 1 for x in DemandList]
			PipelineList.append(Pipeline(DemandList=DemandList))

		## Regular Pipelines
		self.PipelineList = PipelineList

	def GeneratePipelineList2(
		self,
		mice_ratio=0,
		elephant_ratio=100,
		mice_scale=10,
		elephant_scale=100,
	) -> None:
		n_mice, n_elep, eps_mice, eps_elep = mice_ratio, elephant_ratio, mice_scale, elephant_scale

		pls: list[Pipeline] = []
		total_n_pls = n_mice + n_elep

		for i in range(total_n_pls):
			remain_pls = total_n_pls - i
			rnd = random.randrange(0, remain_pls)
			eps_total = 0

			if rnd < n_mice:
				eps_total = eps_mice
				n_mice -= 1
			else:
				eps_total = eps_elep
				n_elep -= 1

			step = eps_total / 100
			pl = []
			for _ in range(self.NumBlock):
				values = numpy.arange(eps_total-step*25, eps_total+step*25, step=step)
				if values.size == 0:
					demand = 0
				else:
					demand = numpy.random.choice(values)
				pl.append(demand)
			pls.append(Pipeline(pl))

		self.PipelineList = pls

	def StartSimulation(self) -> None:
		if self.PipelineList == []:
			self.GeneratePipelineList()
		scheduler: DPFScheduler = DPFScheduler(self.GlobalEpsilon, self.NumberFirstPL, self.NumBlock)
		attacker: BasicAttacker = self.attacker

		if self.verbose == True:
			print("\n---- Scheduling Settings ----")
			print("Global Epsilon:", self.GlobalEpsilon)
			print("Number of the First Pipelines", self.NumberFirstPL)
			print("Number of Blocks", self.NumBlock)
			print("Number of Attack Pipelines", self.NumAtkPL)
			print("\n---- Pipeline Scheduling ----")

		FinishedPipelineList: list[int] = []
		assert(len(self.PipelineList) >= self.NumberFirstPL)
		regular_pipeline_index = 0

		while scheduler.GetTimeslot() < self.NumberFirstPL:
			## First Try to attack
			AtkPipeline = attacker.AttackScheduler(scheduler=scheduler)
			if AtkPipeline != None:
				scheduler.AddToWaitingList(AtkPipeline)
				scheduler.OnPipelineArrival(AtkPipeline)
				FinishedPipelineList += scheduler.OnSchedulerTimer()
				if self.verbose == True:
					print("AtkPipeline:", AtkPipeline.DemandList)
					# print("Time slot", scheduler.GetTimeslot()-1, "\tPipeline", FinishedPipelineList)
					pass
				continue

			Pipeline = self.PipelineList[regular_pipeline_index]
			regular_pipeline_index += 1
			scheduler.AddToWaitingList(Pipeline)
			scheduler.OnPipelineArrival(Pipeline)
			FinishedPipelineList += scheduler.OnSchedulerTimer()
			if self.verbose == True:
				# print("Time slot", scheduler.GetTimeslot()-1, "\tPipeline", FinishedPipelineList)
				pass

		self.attacker = attacker
		self.FinishedPipelineList = FinishedPipelineList

	def GetSimulationResult(self) -> float:
		attacker_budget_sum = self.attacker.CalculateGainedBudget(self.FinishedPipelineList)
		## budget fraction
		attacker_budget_frc = attacker_budget_sum * 1.0 / (self.GlobalEpsilon * self.NumBlock)
		return attacker_budget_frc

	def GetRegularPipelineList(self) -> list:
		return self.PipelineList
