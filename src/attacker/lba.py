from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import config

def PrintThreshold(threshold):
	if not hasattr(PrintThreshold, "has_printed"):
		print("THR:", threshold)
		PrintThreshold.has_printed = True

class Attacker(BasicAttacker):
	"""
	Lowest Budget Attack
		Attack the DPF system with unfixed time slot
			decides whether to attack in every time slot
			chooses the time slot when budget exceeds a threshold
		Generate the AtkPipeline with the minimum budget of all blocks
			to guarantee the allocation
	"""

	THRESHOLD = config.GlobalEpsilon / config.NumAtkPL

	def __init__(self, scheduler: DPFScheduler, NumAtkPL: int) -> None:
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		PrintThreshold(self.THRESHOLD)

	def SetThresholdCoefficient(self, threshold: int) -> None:
		self.THRESHOLD = threshold

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		Main Attack Function
		"""
		## Return None if there is no AtkPipeline left
		if len(self.AtkPipelineList) == self.NumAtkPL:
			return None

		## Return None when the minimum budget is below threshold
		minbudget = min(scheduler.GetUnallocatedBudgetList())

		if self.NumAtkPL - len(self.AtkPipelineList) + scheduler.GetTimeslot() + 1 == scheduler.GetNumberFirstPL():
			AtkPipeline = Pipeline([scheduler.GetBudgetStep()] * scheduler.GetNumberBlock())
			self.AtkPipelineList.append(AtkPipeline)
			return AtkPipeline

		## Budget Threshold
		# budget_threshold = scheduler.GetBudgetStep() * self.THRESHOLD_COEFFICIENT
		if minbudget < self.THRESHOLD:
			return None
		else:
			AtkPipeline = Pipeline([minbudget] * scheduler.GetNumberBlock())
			self.AtkPipelineList.append(AtkPipeline)
			return AtkPipeline
