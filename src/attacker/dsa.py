from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline

class Attacker(BasicAttacker):
	"""
	Dynamic Sequential Attack
	"""

	def __init__(self, scheduler: DPFScheduler, NumAtkPL: int) -> None:
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []

	def Attackable(self, scheduler: DPFScheduler, pipeline_time_slot) -> bool:
		"""
		"""

		pipeline = scheduler.GetPipelineFromList(pipeline_time_slot)
		dominant_share_index = pipeline.GetDominantShareIndex()
		dominant_share = pipeline.GetDominantShare()

		## Intuitive Function Calculation
		remain_budget = \
			(scheduler.GetNumberFirstPL() -  scheduler.GetTimeslot() - 1) * scheduler.GetBudgetStep() + \
			scheduler.GetUnallocatedBudgetList()[dominant_share_index]

		remain_budget -= dominant_share * (self.NumAtkPL - len(self.AtkPipelineList))
		if remain_budget < dominant_share:
			return True

		return False

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		"""

		if len(self.AtkPipelineList) == self.NumAtkPL:
			return None

		attackflag: bool = False
		maxbudget: int = 0
		SortedWaitingPipelineList: list[int] = scheduler.SortWaitingPipelineList()
		UnallocatedBudgetList : list[int] = scheduler.GetUnallocatedBudgetList()
		for block_index in range(scheduler.GetNumberBlock()):
			UnallocatedBudgetList[block_index] += scheduler.GetGlobalEpsilon() // scheduler.GetNumberFirstPL()
		NumBlock: int = len(UnallocatedBudgetList)
		for pipeline_time_slot in SortedWaitingPipelineList:
			pipeline: Pipeline = scheduler.GetPipelineFromList(pipeline_time_slot)

			##
			CanRunFlag: bool = True
			for block_index in range(NumBlock):
				if pipeline.DemandList[block_index] > UnallocatedBudgetList[block_index]:
					CanRunFlag = False
					break
			if CanRunFlag == False:
				continue

			##
			if self.Attackable(scheduler, pipeline_time_slot):
				attackflag: bool = True
				maxbudget = max(pipeline.DemandList)
				break
			else:
				for block_index in range(NumBlock):
					UnallocatedBudgetList[block_index] -= pipeline.DemandList[block_index]

		if attackflag == True:
			DemandList: list[int] = [0] * NumBlock
			for block_index in range(NumBlock):
				if UnallocatedBudgetList[block_index] >= maxbudget:
					DemandList[block_index] = maxbudget - 1 ## minus one to ensure it order is higher
				else:
					DemandList[block_index] = UnallocatedBudgetList[block_index]
			AtkPipeline = Pipeline(DemandList)
			self.AtkPipelineList.append(AtkPipeline)
			return AtkPipeline

		return None
