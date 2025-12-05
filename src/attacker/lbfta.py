from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline

class Attacker(BasicAttacker):
	"""
	Lowest Budget with Fixed Timeslot Attack
		Attack the DPF system with fixed time slot.
		Generate the AtkPipeline with the minimum budget of all blocks
			to guarantee the allocation
	"""

	def __init__(self, NumAtkPL: int) -> None:
		self.NumAtkPL = NumAtkPL
		self.AtkTimeslotList = []
		self.AtkPipelineList = []

	def GenerateAttackTimeslot(self, NumberFirstPL: int, NumAtkPL: int) -> None:
		AtkTimeslotList: list[int] = []
		AtkInterval: int = NumberFirstPL // NumAtkPL
		for i in range(NumAtkPL):
			AtkTimeslotList.append(NumberFirstPL - i * AtkInterval)
		AtkTimeslotList.reverse()
		self.AtkTimeslotList: list[int] = AtkTimeslotList

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		"""
		Main Attack Function
		"""

		## Generate Attack Time Slot List
		if self.AtkTimeslotList == []:
			self.GenerateAttackTimeslot(scheduler.GetNumberFirstPL(), NumAtkPL=self.NumAtkPL)

		## The current time slot is not in the AtkTimeslotList
		## DO NOT ATTACK IN THIS MOMENT
		if scheduler.GetTimeslot() not in self.AtkTimeslotList:
			return None

		## The current time slot is in the AtkTimeslotList
		## ATTACK IN THIS MOMENT
		minbudget = min(scheduler.GetUnallocatedBudgetList())
		AtkPipeline = Pipeline([minbudget] * scheduler.GetNumberBlock())
		self.AtkPipelineList.append(AtkPipeline)
		return AtkPipeline
