from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import config, statistics

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

	def __init__(self, NumAtkPL: int) -> None:
		super().__init__(NumAtkPL)
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		PrintThreshold(self.THRESHOLD)

	def SetThreshold(self, threshold: int) -> None:
		self.THRESHOLD = threshold

	def ThresholdAdjustmentParameter(self, scheduler:DPFScheduler) -> float:
		"""
		Dynamic adjust the threshold
		"""
		NumUnusedAtkPL = self.NumAtkPL - len(self.AtkPipelineList) ## Number of Unused Adversarial Pipeline
		TimeSlotLeft = scheduler.GetNumberFirstPL() - scheduler.GetTimeslot()
		adj: float = (self.NumAtkPL / scheduler.GetNumberFirstPL()) / (NumUnusedAtkPL / TimeSlotLeft) * 0.5 ## Adjustment
		return adj

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		Main Attack Function
			1. Dynamically adjust the threshold
			2. Aggressively plus epsilon^{FS} for every demand
		"""
		## Return None if there is no AtkPipeline left
		if len(self.AtkPipelineList) == self.NumAtkPL:
			return None

		UnallocatedBudgetList = scheduler.GetUnallocatedBudgetList()
		## Return None when the minimum budget is below threshold
		minbudget = min(UnallocatedBudgetList)

		if scheduler.GetTimeslot() + self.NumAtkPL - len(self.AtkPipelineList) >= scheduler.GetNumberFirstPL():
			AtkPipeline = Pipeline([scheduler.GetBudgetStep()] * scheduler.GetNumberBlock())
			self.AtkPipelineList.append(AtkPipeline)
			return AtkPipeline

		## Budget Threshold
		if minbudget < self.THRESHOLD * self.ThresholdAdjustmentParameter(scheduler):
			return None
		else:
			DemandList = [minbudget + scheduler.GetBudgetStep()] * scheduler.GetNumberBlock()
			AtkPipeline = Pipeline(DemandList)
			self.AtkPipelineList.append(AtkPipeline)
			return AtkPipeline
