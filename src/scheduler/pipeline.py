
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
