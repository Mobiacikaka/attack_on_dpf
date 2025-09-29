from simulator import Simulator
from attacker.lbaft import Attacker as LBFTAttacker

def main():
	simulator = Simulator(
		GlobalEpsilon=40*100, # int(float(input()) * 100),
		NumberFirstPL=40,   # int(input()),
		NumBlock=10,        # int(input()),
		PipelineList=[],    # [],
		NumAtkPL=8,         # int(input()),
		verbose=True,
	)
	simulator.SetAttacker(LBFTAttacker)
	simulator.StartSimulation()

if __name__ == '__main__':
	main()
