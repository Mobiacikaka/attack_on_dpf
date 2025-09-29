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
		self.PipelineList: list = PipelineList
		self.NumAtkPL: int = NumAtkPL
		self.verbose: bool = verbose
		self.AttackerClass: type[BasicAttacker] = BasicAttacker

	def SetAttacker(self, AttackerClass: type[BasicAttacker]) -> None:
		self.AttackerClass = AttackerClass

	def GeneratePipelineList(
		self,
		mice_ratio=50,
		elephant_ratio=50,
		mice_scale=10,
		elephant_scale=100,
	)  -> list[Pipeline]:
		"""
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

		# self.PipelineList = PipelineList
		for pl in PipelineList:
			print(pl.DemandList)
		return PipelineList

	def StartSimulation(self) -> None:
		if self.PipelineList == []:
			self.PipelineList = self.GeneratePipelineList()
		scheduler: DPFScheduler = DPFScheduler(self.GlobalEpsilon, self.NumberFirstPL, self.NumBlock)
		attacker: BasicAttacker = self.AttackerClass(scheduler=scheduler, NumAtkPL=self.NumAtkPL)

		if self.verbose == True:
			print("\n---- Scheduling Settings ----")
			print("Global Epsilon:", self.GlobalEpsilon)
			print("Number of the First Pipelines", self.NumberFirstPL)
			print("Number of Blocks", self.NumBlock)
			print("Number of Attack Pipelines", self.NumAtkPL)
			print("\n---- Pipeline Scheduling ----")

		for Pipeline in self.PipelineList:
			## First Try to attack
			AtkPipeline = attacker.AttackScheduler(scheduler=scheduler)
			if AtkPipeline != None:
				scheduler.AddToWaitingList(AtkPipeline)
				scheduler.OnPipelineArrival(AtkPipeline)
				FinishedPipelineList: list = scheduler.OnSchedulerTimer()
				if self.verbose == True:
					print("AtkPipeline:", AtkPipeline.DemandList)
					print("Time slot", scheduler.GetTimeslot()-1, "\tPipeline", FinishedPipelineList)

			scheduler.AddToWaitingList(Pipeline)
			scheduler.OnPipelineArrival(Pipeline)
			FinishedPipelineList: list = scheduler.OnSchedulerTimer()
			if self.verbose == True:
				print("Time slot", scheduler.GetTimeslot()-1, "\tPipeline", FinishedPipelineList)
