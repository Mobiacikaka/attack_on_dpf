from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import numpy
import config

class Attacker(BasicAttacker):
	"""
	Random Attack
	"""

	def __init__(self, NumAtkPL: int) -> None:
		super().__init__(NumAtkPL)
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		self.AtkTimeslotList = []
		self.RegularPipelineList = []

	def SetRegularPipelineList(self, PipelineList):
		self.RegularPipelineList = PipelineList

	def GenerateAtkTimeslotList(self):
		self.AtkTimeslotList: list = numpy.random.choice(list(range(config.NumberFirstPL)), self.NumAtkPL).tolist()
		self.AtkTimeslotList.sort()

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		if len(self.AtkTimeslotList) == 0:
			self.GenerateAtkTimeslotList()

		TimeSlot= scheduler.GetTimeslot()
		if TimeSlot in self.AtkTimeslotList:
			self.AtkPipelineList.append(self.RegularPipelineList[TimeSlot])

		return None
