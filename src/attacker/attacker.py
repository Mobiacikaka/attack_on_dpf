from scheduler.dpf import DPFScheduler
from scheduler.pipeline import Pipeline

class BasicAttacker:
	"""
	Basic Attacker
		DO NOTHING WHEN ATTACKING
	"""

	AtkPipelineList: list[Pipeline] = []

	def __init__(self, scheduler: DPFScheduler, NumAtkPL: int) -> None:
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
		for AtkPipeline in self.AtkPipelineList:
			if AtkPipeline.TimeSlot in FinishedPipelineList:
				budget_sum += AtkPipeline.BudgetSum()
		return budget_sum
