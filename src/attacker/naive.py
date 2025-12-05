from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import config

class Attacker(BasicAttacker):
	"""
	Naive Greedy
	"""

	def __init__(self, NumAtkPL: int) -> None:
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		self.AtkTimeslotList = []
		self.RegularPipelineList = []

	def SetRegularPipelineList(self, PipelineList):
		self.RegularPipelineList = PipelineList

	def GenerateAtkPipeline(self):
		assert(len(self.RegularPipelineList) >= config.NumberFirstPL)

		while len(self.AtkPipelineList) < self.NumAtkPL:
			AtkTimeslot = 0
			AtkPipeline_best = Pipeline()

			scheduler = DPFScheduler(config.GlobalEpsilon, config.NumberFirstPL, config.NumBlock)
			for TimeSlot in range(config.NumberFirstPL):
				if TimeSlot in self.AtkTimeslotList:
					continue
				AtkPipeline_tmp = self.MaximizeAdversary(scheduler)
				if AtkPipeline_tmp.BudgetSum() > AtkPipeline_best.BudgetSum():
					AtkTimeslot = TimeSlot
					AtkPipeline_best = AtkPipeline_tmp
				scheduler.AddToWaitingList(self.RegularPipelineList[TimeSlot])
				scheduler.OnPipelineArrival(self.RegularPipelineList[TimeSlot])
				scheduler.OnSchedulerTimer()
			self.RegularPipelineList.insert(AtkTimeslot, AtkPipeline_best)
			for i in range(len(self.AtkTimeslotList)):
				if self.AtkTimeslotList[i] >= AtkTimeslot:
					self.AtkTimeslotList[i] += 1
			self.AtkTimeslotList.append(AtkTimeslot)
			self.AtkPipelineList.append(AtkPipeline_best)

		self.AtkPipelineList = [x for _, x in sorted(zip(self.AtkTimeslotList, self.AtkPipelineList))]
		self.AtkTimeslotList.sort()

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		if len(self.AtkTimeslotList) == 0:
			self.GenerateAtkPipeline()

		if scheduler.GetTimeslot() in self.AtkTimeslotList:
			N = len(self.AtkPipelineList)
			AtkPipeline = self.AtkPipelineList[N - self.NumAtkPL]
			self.NumAtkPL -= 1
			return AtkPipeline

		return None
