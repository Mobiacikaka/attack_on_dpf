from src.scheduler.dpf import DPFScheduler

class Attacker:
	"""
	Attack the DPF system with fixed time slot.
	Generate the AtkPipeline with the minimum budget of all blocks
		to guarantee the allocation
	"""

	def __init__(self) -> None:
		pass

	def GenerateAttackTimeslot(self, NumberFirstPL: int, NumAtkPL: int) -> None:
		AtkTimeslotList: list[int] = []
		AtkInterval: int = NumberFirstPL // NumAtkPL
		for i in range(NumAtkPL):
			AtkTimeslotList.append(NumberFirstPL - i * AtkInterval)
		AtkTimeslotList.reverse()
		self.AtkTimeslotList: list[int] = AtkTimeslotList

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | list[int] :
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
		return [minbudget] * scheduler.GetNumberBlock()
