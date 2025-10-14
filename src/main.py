from simulator import Simulator
from attacker.lbfta import Attacker as LBFTAttacker
from attacker.lba import Attacker as LBAttacker
from attacker.dsa import Attacker as DSAttacker
import numpy

def main(verbose: bool=False):
	simulator = Simulator(
		GlobalEpsilon=40*100,	# int(float(input()) * 100),
		NumberFirstPL=100,   	# int(input()),
		NumBlock=10,         	# int(input()),
		PipelineList=[],     	# [],
		NumAtkPL=30,         	# int(input()),
		verbose=verbose,
	)

	LBFAT_result_list = []
	DSA_result_list = []
	LBA_result_list = []

	for _ in range(100):
		simulator.GeneratePipelineList(mice_ratio=75, elephant_ratio=25)

		if verbose == True:
			print("\n##### DSA #####")
		simulator.SetAttacker(DSAttacker)
		simulator.StartSimulation()
		DSA_result_list.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### LBFTAttacker #####")
		simulator.SetAttacker(LBFTAttacker)
		simulator.StartSimulation()
		LBFAT_result_list.append(simulator.GetSimulationResult())

		if verbose == True:
			print("\n##### LBAttacker #####")
		simulator.SetAttacker(LBAttacker)
		simulator.StartSimulation()
		LBA_result_list.append(simulator.GetSimulationResult())

	print("DSA\t", numpy.mean(DSA_result_list))
	print("LBFAT\t", numpy.mean(LBFAT_result_list))
	print("LBA\t", numpy.mean(LBA_result_list))

if __name__ == '__main__':
	main(verbose=False)
