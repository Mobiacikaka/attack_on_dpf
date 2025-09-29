from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline

class Attacker(BasicAttacker):
	"""
	Lowest Budget Attack with Fixed Timeslot
		Attack the DPF system with fixed time slot.
		Generate the AtkPipeline with the minimum budget of all blocks
			to guarantee the allocation
	"""

	def __init__(self, scheduler: DPFScheduler, NumAtkPL: int) -> None:
		self.AtkTimeslotList: list[int] = []
		self.NumAtkPL = NumAtkPL
		self.GenerateAttackTimeslot(scheduler.GetNumberFirstPL(), NumAtkPL=self.NumAtkPL)

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

		## The current time slot is not in the AtkTimeslotList
		## DO NOT ATTACK IN THIS MOMENT
		if scheduler.GetTimeslot() not in self.AtkTimeslotList:
			return None

		## The current time slot is in the AtkTimeslotList
		## ATTACK IN THIS MOMENT
		UnallocatedBudgetList = scheduler.GetUnallocatedBudgetList()
		minbudget = min(UnallocatedBudgetList)
		return Pipeline([minbudget] * scheduler.GetNumberBlock())
