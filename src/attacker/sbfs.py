from scheduler.dpf import DPFScheduler
from attacker.attacker import BasicAttacker
from scheduler.pipeline import Pipeline
import config, copy, math
import pdb

class Attacker(BasicAttacker):
	def __init__(self, NumAtkPL: int) -> None:
		super().__init__(NumAtkPL)
		self.NumAtkPL = NumAtkPL
		self.AtkPipelineList = []
		self.AtkTimeslotList = []
		self.RegularPipelineList = []
		self.CheckFullyAllocationFlag = True

	def SetRegularPipelineList(self, PipelineList: list[Pipeline]):
		self.RegularPipelineList = copy.deepcopy(PipelineList)

	def SegmentedBruteForceSearch(self, ):
		assert(len(self.RegularPipelineList) != 0)
		scheduler0: DPFScheduler = DPFScheduler(config.GlobalEpsilon, config.NumberFirstPL, config.NumBlock)
		# pdb.set_trace()

		K1 = 0
		K2 = self.NumAtkPL

		segment_start = 0
		segment_end = 0
		while K2 > 0:

			## Update segment start and end
			segment_start = segment_end
			segment_end += (config.NumberFirstPL-config.NumAtkPL) / config.NumAtkPL
			AtkPipeline_best = Pipeline([])
			AtkTimeslot = 0

			scheduler = copy.deepcopy(scheduler0)

			for TimeSlot in range(
				int(segment_start)+K1,
				int(segment_end)+K1+1
			):
				if TimeSlot > config.NumberFirstPL:
					break

				## Tries to maximize AtkPipeline before new regular pipeline came
				AtkPipeline_tmp = self.MaximizeAdversary(scheduler)
				if AtkPipeline_tmp.BudgetSum() > AtkPipeline_best.BudgetSum():
					AtkPipeline_best = AtkPipeline_tmp
					AtkTimeslot = TimeSlot
				# self.CheckAllocation(scheduler, AtkPipeline_tmp, TimeSlot)

				## Allocate the regular pipeline
				scheduler.AddToWaitingList(self.RegularPipelineList[TimeSlot])
				scheduler.OnPipelineArrival(self.RegularPipelineList[TimeSlot])
				scheduler.OnSchedulerTimer()

			## Insert the AtkPipeline to RegularPipelineList
			self.RegularPipelineList.insert(AtkTimeslot, AtkPipeline_best)
			self.AtkTimeslotList.append(AtkTimeslot)
			self.AtkPipelineList.append(AtkPipeline_best)

			## Update the scheduler0 state
			FinishedPipelineList = []
			for TimeSlot in range(
				int(segment_start)+K1,
				int(segment_end)+K1+1
			):
				scheduler0.AddToWaitingList(self.RegularPipelineList[TimeSlot])
				scheduler0.OnPipelineArrival(self.RegularPipelineList[TimeSlot])
				assert(self.RegularPipelineList[TimeSlot].GetTimeSlot() == TimeSlot)
				FinishedPipelineList += scheduler0.OnSchedulerTimer()
			assert(AtkTimeslot in FinishedPipelineList)

			K1 += 1
			K2 -= 1
			## continue the loop

		return

	def AttackScheduler(self, scheduler: DPFScheduler) -> None | Pipeline:
		if len(self.AtkTimeslotList) == 0:
			self.SegmentedBruteForceSearch()

		TimeSlot = scheduler.GetTimeslot()
		if TimeSlot in self.AtkTimeslotList:
			pipeline_index = self.AtkTimeslotList.index(TimeSlot)
			return self.AtkPipelineList[pipeline_index]

		return None
