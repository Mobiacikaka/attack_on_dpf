from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import config, copy

class Attacker(BasicAttacker):
	"""
	Naive Greedy
	"""

	def __init__(self, NumAtkPL: int) -> None:
		super().__init__(NumAtkPL)
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		self.AtkTimeslotList = []
		self.RegularPipelineList = []

	def SetRegularPipelineList(self, PipelineList):
		self.RegularPipelineList = copy.deepcopy(PipelineList)

	def Check(self, scheduler: DPFScheduler, AtkPipeline: Pipeline, AtkTimeslot):
		scheduler = copy.deepcopy(scheduler)
		scheduler.AddToWaitingList(AtkPipeline)
		scheduler.OnPipelineArrival(AtkPipeline)

		print(AtkPipeline.GetTimeSlot(), AtkTimeslot)
		# print(AtkPipeline.DemandList)
		assert(AtkPipeline.GetTimeSlot() == AtkTimeslot)

		FinishedPipelineList = scheduler.OnSchedulerTimer()
		assert(AtkTimeslot in FinishedPipelineList)

	def GenerateAtkPipeline(self):
		assert(len(self.RegularPipelineList) >= config.NumberFirstPL)

		K = self.NumAtkPL
		while K > 0:
			AtkTimeslot = 0
			AtkPipeline_best = Pipeline()

			scheduler = DPFScheduler(config.GlobalEpsilon, config.NumberFirstPL, config.NumBlock)
			for TimeSlot in range(config.NumberFirstPL - K + 1):
				if TimeSlot not in self.AtkTimeslotList:
				## Tries to maximize the AtkPipeline at this time slot
					AtkPipeline_tmp = self.MaximizeAdversary(scheduler)
					if AtkPipeline_tmp.BudgetSum() > AtkPipeline_best.BudgetSum():
						AtkTimeslot = TimeSlot
						AtkPipeline_best = AtkPipeline_tmp
				scheduler.AddToWaitingList(self.RegularPipelineList[TimeSlot])
				scheduler.OnPipelineArrival(self.RegularPipelineList[TimeSlot])
				scheduler.OnSchedulerTimer()

			##
			self.RegularPipelineList.insert(AtkTimeslot, AtkPipeline_best)
			for i in range(len(self.AtkTimeslotList)):
				if self.AtkTimeslotList[i] > AtkTimeslot:
					self.AtkTimeslotList[i] += 1
				elif self.AtkTimeslotList[i] == AtkTimeslot:
					assert(0)
			self.AtkTimeslotList.append(AtkTimeslot)
			self.AtkPipelineList.append(AtkPipeline_best)

			K -= 1

		self.AtkPipelineList = [x for _, x in sorted(zip(self.AtkTimeslotList, self.AtkPipelineList))]
		self.AtkTimeslotList.sort()

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		if len(self.AtkTimeslotList) == 0:
			self.GenerateAtkPipeline()

		AtkTimeslot = scheduler.GetTimeslot()
		if AtkTimeslot in self.AtkTimeslotList:
			pipeline_index= self.AtkTimeslotList.index(AtkTimeslot)
			AtkPipeline = self.AtkPipelineList[pipeline_index]
			# print(scheduler.GetUnallocatedBudgetList())
			return AtkPipeline

		return None
