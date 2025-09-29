from simulator import Simulator

def main():
	# simulator = Simulator(
	# 	GlobalEpsilon=int(float(input()) * 100),
	# 	NumberFirstPL=int(input()),
	# 	NumBlock=int(input()),
	# 	PipelineList=[],
	# 	NumAtkPL=int(input()),
	# 	verbose=True,
	# )
	simulator = Simulator(
		GlobalEpsilon=40*3,
		NumberFirstPL=40,
		NumBlock=10,
		PipelineList=[],
		NumAtkPL=8,
		verbose=True
	)
	simulator.GeneratePipelineList()
	simulator.StartSimulation()

if __name__ == '__main__':
	main()
