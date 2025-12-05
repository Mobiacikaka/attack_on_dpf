from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import config

class Attacker(BasicAttacker):
	def __init__(self, NumAtkPL: int) -> None:
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		self.AtkTimeslotList = []
		self.RegularPipelineList = []

	def SetRegularPipelineList(self, PipelineList):
		self.RegularPipelineList = PipelineList

	def SegmentedBruteForceSearch(self, ):
		assert(len(self.RegularPipelineList) != 0)
		scheduler0: DPFScheduler = DPFScheduler(config.GlobalEpsilon, config.NumberFirstPL, config.NumBlock)

		segment_start = 0
		segment_end = 0
		for segment_index in range(config.NumAtkPL):
			segment_start= segment_end
			segment_end += (config.NumberFirstPL - config.NumAtkPL) / config.NumAtkPL
			DemandList = []
			AtkTimeslot = 0

			# for AtkTimeslot in range(int(segment_start)+k1, int(end)+k1+1)
		return

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		return None
		if len(self.AtkTimeslotList) == 0:
			self.SegmentedBruteForceSearch()
		return None
