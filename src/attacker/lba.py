from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline

class Attacker(BasicAttacker):
	"""
	Lowest Budget Attack
		Attack the DPF system with unfixed time slot
			decides whether to attack in every time slot
			chooses the time slot when budget exceeds a threshold
		Generate the AtkPipeline with the minimum budget of all blocks
			to guarantee the allocation
	"""

	def __init__(self, scheduler: DPFScheduler, NumAtkPL: int) -> None:
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		Main Attack Function
		"""
		## Return None if there is no AtkPipeline left
		if len(self.AtkPipelineList) == self.NumAtkPL:
			return None

		if self.NumAtkPL - len(self.AtkPipelineList) == scheduler.GetNumberFirstPL():
			return Pipeline([scheduler.GetGlobalEpsilon() // scheduler.GetNumberFirstPL()] * scheduler.GetNumberBlock())

		## Budget Threshold
		budget_threshold = scheduler.GetGlobalEpsilon() // scheduler.GetNumberFirstPL() * 2

		## Return None when the minimum budget is below threshold
		minbudget = min(scheduler.GetUnallocatedBudgetList())
		if minbudget < budget_threshold:
			return None
		else:
			AtkPipeline = Pipeline([minbudget] * scheduler.GetNumberBlock())
			self.AtkPipelineList.append(AtkPipeline)
			return AtkPipeline
