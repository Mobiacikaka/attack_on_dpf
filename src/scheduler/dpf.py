from scheduler.pipeline import Pipeline

import copy
import config

class DPFScheduler:
	"""
	Suppose the minimum epsilon accepted is 0.01,
	then the float in the system is multiply of 100,
	to prevent the float number accuracy issues.
	"""

	def __init__(self, GlobalEpsilon: int, NumberFirstPL: int, NumBlock: int) -> None:
		self.GlobalEpsilon = GlobalEpsilon
		self.NumberFirstPL = NumberFirstPL
		self.NumBlock = NumBlock

		self.GlobalBudget: list[int] = []
		self.UnalloBudget: list[int] = []
		self.AllocaBudget: list[int] = []
		self.ConsumBudget: list[int] = []

		self.TimeSlot: int = 0

		## Timeslot, Pipeline
		self.WaitingPipelineList: dict[int, Pipeline] = {}
		self.CompletedPipelineList: list[int] = []

		for _ in range(self.NumBlock):
			self.OnDataBlockCreation()

		## Defense Flag
		if config._lambda == 0.0:
			self.DefensiveFlag: bool = False
			self.Lambda = 0.0
		else:
			self.DefensiveFlag: bool = True
			self.Lambda = config._lambda

	def OnDataBlockCreation(self) -> None:
		self.GlobalBudget.append(self.GlobalEpsilon)
		self.UnalloBudget.append(0)
		self.AllocaBudget.append(0)
		self.ConsumBudget.append(0)

	def AddToWaitingList(self, pl: Pipeline) -> None:
		"""
		Add pipeline to waiting list
		Tuple List
		(time, Pipeline)
		...
		(time, Pipeline)
		"""
		assert(len(pl.DemandList) == self.NumBlock)
		self.WaitingPipelineList[self.TimeSlot] = pl
		pl.SetTimeSlot(self.TimeSlot)

	def OnPipelineArrival(self, pl: Pipeline) -> None:
		"""
		Release privacy budget block into the UnalloBudget list
		"""
		for block_index in range(self.NumBlock):
			if pl.DemandList[block_index] > 0:
				UnallocatedBudget_j = self.GlobalBudget[block_index] - self.ConsumBudget[block_index]
				self.UnalloBudget[block_index] = min(
					UnallocatedBudget_j,
					self.UnalloBudget[block_index]+self.GlobalBudget[block_index]//self.NumberFirstPL
				)

	def GetSortedDemandRatio(self, pl: Pipeline) -> list[float]:
		demandratio: list[float] = [0.0 for _ in range(self.NumBlock)]
		for block_index in range(self.NumBlock):
			demandratio[block_index] = pl.DemandList[block_index] / self.GlobalBudget[block_index]
		demandratio.sort(reverse=True)
		if self.DefensiveFlag == True:
			## Linear
			# demandratio = [x * pl.GetTimeSlot() / self.NumberFirstPL for x in demandratio]

			## Exponential
			demandratio = [
				x * pow(self.Lambda, self.TimeSlot - pl.GetTimeSlot())
				for x in demandratio
			]

		return demandratio

	def GetPipelineFromList(self, timeslot: int) -> Pipeline:
		pipeline = self.WaitingPipelineList.get(timeslot)
		assert(pipeline != None)
		return pipeline

	def SortWaitingPipelineList(self) -> list[int]:
		"""
		Return the time slot list sorted by pipeline's demand ratio
		"""
		return sorted(
			self.WaitingPipelineList,
			key=lambda timeslot: self.GetSortedDemandRatio(self.GetPipelineFromList(timeslot))
		)

	def CanRun(self, pl: Pipeline) -> bool:
		"""
		Check if pipeline have less budget than Unallocated Budget
		"""
		for block_index in range(self.NumBlock):
			if pl.DemandList[block_index] > self.UnalloBudget[block_index]:
				return False
		return True

	def AllocatePipeline(self, pl: Pipeline) -> None:
		"""
		Allocate budget to pipeline
		"""
		for block_index in range(self.NumBlock):
			self.UnalloBudget[block_index] -= pl.DemandList[block_index]
			self.AllocaBudget[block_index] += pl.DemandList[block_index]
		return

	def RunPipeline(self, pl: Pipeline) -> bool:
		"""
		Remove Privacy Budget from Allocated Budget;
		Add Privacy Budget to Consumed Budget;
		Pop pipeline from Waiting List
		Add pipeline to Complete List
		Return True if pipeline is ran succesfully.
		"""
		for block_index in range(self.NumBlock):
			self.AllocaBudget[block_index] -= pl.DemandList[block_index]
			self.ConsumBudget[block_index] += pl.DemandList[block_index]
		self.WaitingPipelineList.pop(pl.TimeSlot)
		self.CompletedPipelineList.append(pl.TimeSlot)
		return True

	def OnSchedulerTimer(self):
		"""
		Scheduling system
		"""
		SortedWaitingPipelineList: list[int] = self.SortWaitingPipelineList()
		pipeline_index = 0
		## The time slot of finished pipelines
		FinishedPipelineList: list[int] = []
		while pipeline_index < len(SortedWaitingPipelineList):
			pipeline_time_slot: int = SortedWaitingPipelineList[pipeline_index] # comment
			pipeline: Pipeline = self.GetPipelineFromList(pipeline_time_slot)
			if self.CanRun(pipeline):
				self.AllocatePipeline(pipeline)
				self.RunPipeline(pipeline)
				FinishedPipelineList.append(pipeline_time_slot)
			pipeline_index += 1
		self.TimeSlot += 1
		return FinishedPipelineList

	## Public Functions
	def GetNumberFirstPL(self) -> int:
		"""
		Return the number of pipelines which DPF scheduler will release new privacy block
		"""
		return self.NumberFirstPL

	def GetNumberBlock(self) -> int:
		"""
		Return the number of data blocks
		"""
		return self.NumBlock

	def GetTimeslot(self) -> int:
		"""
		Return the current time of the scheduler
		"""
		return self.TimeSlot

	def GetUnallocatedBudgetList(self) -> list[int]:
		"""
		Return the copy of Unallocated Budget List
		"""
		return copy.deepcopy(self.UnalloBudget)

	def GetGlobalEpsilon(self) -> int:
		return self.GlobalEpsilon

	def GetBudgetStep(self) -> int:
		return self.GlobalEpsilon // self.NumberFirstPL

	def GetWaitingPipelineList(self) -> dict:
		return self.WaitingPipelineList
