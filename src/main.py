import config
from simulator import Simulator
from attacker.lbfta import Attacker as LBFTAttacker
from attacker.lba import Attacker as LBAttacker
from attacker.dsa import Attacker as DSAttacker
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

	LBFAT_result_list = []
	DSA_result_list = []
	LBA_result_list = []

	for _ in range(config.times):
		simulator.GeneratePipelineList(
			mice_ratio=config.mice_ratio,
			mice_scale=config.mice_scale,
			elephant_ratio=config.elephant_ratio,
			elephant_scale=config.elephant_scale,
		)

		# if verbose == True:
		# 	print("\n##### DSA #####")
		# simulator.SetAttacker(DSAttacker)
		# simulator.StartSimulation()
		# DSA_result_list.append(simulator.GetSimulationResult())

		# if verbose == True:
		# 	print("\n##### LBFTAttacker #####")
		# simulator.SetAttacker(LBFTAttacker)
		# simulator.StartSimulation()
		# LBFAT_result_list.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### LBAttacker #####")
		simulator.SetAttacker(LBAttacker)
		simulator.StartSimulation()
		LBA_result_list.append(simulator.GetSimulationResult())

	# print("DSA:", numpy.mean(DSA_result_list))
	# print("LBFAT\t", numpy.mean(LBFAT_result_list))
	print("LBA:", numpy.mean(LBA_result_list))

if __name__ == '__main__':
	main(
		config.GlobalEpsilon,
		config.NumberFirstPL,
		config.NumBlock,
		config.PipelineList,
		config.NumAtkPL,
		verbose=config.verbose,
	)
