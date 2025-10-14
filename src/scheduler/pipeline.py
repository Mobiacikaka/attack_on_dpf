
class Pipeline:
	def __init__(self, DemandList: list[int]) -> None:
		self.TimeSlot: int = -1
		self.NumBlock: int = 0 ## Number of data blocks
		self.DemandList: list[int] = [] ## Demands for N data blocks

		self.NumBlock = len(DemandList)
		self.DemandList = DemandList

	def SetTimeSlot(self, timeslot: int) -> None:
		assert(timeslot >= 0)
		self.TimeSlot = timeslot
		return

	def GetTimeSlot(self) -> int:
		return self.TimeSlot

	def BudgetSum(self) -> int:
		return sum(self.DemandList)

	def GetDominantShare(self) -> int:
		return max(self.DemandList)

	def GetDominantShareIndex(self) -> int:
		return self.DemandList.index(self.GetDominantShare())
