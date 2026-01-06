import config
from scheduler.pipeline import Pipeline
from simulator import Simulator
from attacker.lba import Attacker as LBAttacker
from attacker.dsa import Attacker as DSAttacker
from attacker.sbfs import Attacker as SBFSAttacker
from attacker.naive import Attacker as NaiveAttacker
from attacker.random import Attacker as RandomAttacker
from attacker.tmp_attacker_1 import Attacker as TimeDecayAttacker
from scheduler.dpf import DPFScheduler
import numpy

def main(
	GlobalEpsilon: int,
	NumberFirstPL: int,
	NumBlock: int,
	PipelineList: list,
	NumAtkPL: int,
	verbose: bool=False,
):
	"""
	Run only one setting
	"""
	simulator = Simulator(
		GlobalEpsilon=GlobalEpsilon,
		NumberFirstPL=NumberFirstPL,
		NumBlock=NumBlock,
		PipelineList=PipelineList,
		NumAtkPL=NumAtkPL,
		verbose=verbose,
	)

	config.PrintConfig()

	result_list_0 = []
	result_list_1 = []
	result_list_2 = []
	result_list_3 = []
	result_list_4 = []

	result_list_tmp = []

	for _ in range(config.times):
		simulator.GeneratePipelineList(
			mice_ratio=config.mice_ratio,
			mice_scale=config.mice_scale,
			elephant_ratio=config.elephant_ratio,
			elephant_scale=config.elephant_scale,
		)

		# if verbose == True:
		# 	print("\n##### Sequential Heuristic #####")
		# attacker = DSAttacker(NumAtkPL)
		# simulator.SetAttacker(attacker)
		# simulator.StartSimulation()
		# result_list_0.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### Threshold Triggered #####")
		attacker = LBAttacker(NumAtkPL)
		simulator.SetAttacker(attacker)
		simulator.StartSimulation()
		result_list_1.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### Segmented Brute-Force #####")
		attacker = SBFSAttacker(NumAtkPL)
		attacker.SetRegularPipelineList(simulator.GetRegularPipelineList())
		simulator.SetAttacker(attacker)
		simulator.StartSimulation()
		result_list_2.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### Naive Greedy #####")
		attacker = NaiveAttacker(NumAtkPL)
		attacker.SetRegularPipelineList(simulator.GetRegularPipelineList())
		simulator.SetAttacker(attacker)
		simulator.StartSimulation()
		result_list_3.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### Naive Greedy #####")
		attacker = RandomAttacker(NumAtkPL)
		attacker.SetRegularPipelineList(simulator.GetRegularPipelineList())
		simulator.SetAttacker(attacker)
		simulator.StartSimulation()
		result_list_4.append(simulator.GetSimulationResult())

	# print("Sequential Heuristic:", numpy.mean(result_list_0), numpy.std(result_list_0))
	print("Threshold-Triggered(Aggr+D-Thr):", numpy.mean(result_list_1), numpy.std(result_list_1))
	print("Segmented Brute Force:", numpy.mean(result_list_2), numpy.std(result_list_2))
	print("Naive Greedy:", numpy.mean(result_list_3), numpy.std(result_list_3))
	print("Random:", numpy.mean(result_list_4), numpy.std(result_list_4))

if __name__ == '__main__':
	numpy.random.seed(0)
	main(
		config.GlobalEpsilon,
		config.NumberFirstPL,
		config.NumBlock,
		config.PipelineList,
		config.NumAtkPL,
		verbose=config.verbose,
	)
