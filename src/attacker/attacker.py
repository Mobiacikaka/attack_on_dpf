from scheduler.dpf import DPFScheduler
from scheduler.pipeline import Pipeline
import copy
import config

class BasicAttacker:
	"""
	Basic Attacker
		DO NOTHING WHEN ATTACKING
	"""

	AtkPipelineList: list[Pipeline] = []

	def __init__(self, NumAtkPL: int) -> None:
		self.NumAtkPL: int = NumAtkPL
		self.AtkPipelineList = []

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		Main Attack Function
		"""

		## DO NOTHING
		return None

	## Public Functions
	def GetAtkTimeslotList(self) -> list[int]:
		AtkTimeslotList = []
		for AtkPipeline in self.AtkPipelineList:
			AtkTimeslotList.append(AtkPipeline.TimeSlot)
		return AtkTimeslotList

	def CalculateGainedBudget(self, FinishedPipelineList: list[int]) -> int:
		budget_sum: int = 0
		NumReceiveAllocation : int = 0
		for AtkPipeline in self.AtkPipelineList:
			if AtkPipeline.TimeSlot in FinishedPipelineList:
				budget_sum += AtkPipeline.BudgetSum()
				NumReceiveAllocation += 1
				# print(f"Atk{AtkPipeline.TimeSlot}", AtkPipeline.DemandList)
		# print(self.NumAtkPL, '/', NumReceiveAllocation)
		return budget_sum

	def SetRegularPipelineList(self):
		assert(0) ## NOT IMPLEMENTED
		return

	def MaximizeAdversary(self, scheduler: DPFScheduler):
		"""
		At the current time slot
		Brute force search all the possible demand vector for adversary pipeline
		Greedily choose a best one
		"""
		scheduler = copy.deepcopy(scheduler)
		UnallocatedBudgetList = scheduler.GetUnallocatedBudgetList()
		for block_index in range(config.NumBlock):
			UnallocatedBudgetList[block_index] += config.GlobalEpsilon // config.NumberFirstPL

		SortedWaitingPipelineList: list = scheduler.SortWaitingPipelineList()
		RegularFlag = False

		DemandList = []
		for pipeline_index in SortedWaitingPipelineList:
			if sum(UnallocatedBudgetList) <= sum(DemandList):
				## the allocation afterwards cannot be higher
				break

			## If the regular_pipeline not canrun, then its DS is not decisive
			regular_pipeline = scheduler.GetPipelineFromList(pipeline_index)
			CanRunFlag = True
			for block_index in range(config.NumBlock):
				if regular_pipeline.DemandList[block_index] > UnallocatedBudgetList[block_index]:
					CanRunFlag = False
					break
			if not CanRunFlag:
				continue

			RegularFlag = True
			dominant_share = regular_pipeline.GetDominantShare()
			DemandList_tmp: list[int] = []
			for block_index in range(config.NumBlock):
				if dominant_share <= UnallocatedBudgetList[block_index]:
					DemandList_tmp.append(dominant_share - 1)
				else:
					DemandList_tmp.append(UnallocatedBudgetList[block_index])

			if sum(DemandList_tmp) > sum(DemandList):
				DemandList = DemandList_tmp

			for block_index in range(config.NumBlock):
				UnallocatedBudgetList[block_index] -= regular_pipeline.DemandList[block_index]

		if not RegularFlag:
			DemandList = UnallocatedBudgetList

		return Pipeline(DemandList)
