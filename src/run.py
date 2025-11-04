import subprocess

def run():
	args = [
		(
			int(step * NumberFirstPL * 100),
			NumberFirstPL,
			NumBlock,
			int(K_ratio * NumberFirstPL),
			mice_ratio,
			mice_scale,
			elephant_ratio,
			elephant_scale,
			times
		)
		for step in [0.5, 0.75, 1.0, 2.0, 3.0]
		for NumBlock in range(5, 31, 5)
		for NumberFirstPL in range(50, 251, 50)
		for K_ratio in [0.1, 0.2, 0.3, 0.4, 0.5]
		for mice_scale in [10]
		for elephant_scale in [100]
		for mice_ratio, elephant_ratio in [(75, 25), (0, 100)]
		for times in [1000]
	]

	outputfile = open("result.csv", "w")
	outputfile.write("GlobalEpsilon,NumberFirstPL,NumBlock,NumAtkPL,mice_ratio,mice_scale,elephant_ratio,elephant_scale,result\n")
	for arg in args:
		input_str = ""
		for par in arg:
			input_str = input_str + f"{par}\n"

		print("Running")
		print(input_str)

		result = subprocess.run(["python", "main.py"], input=input_str, capture_output=True, text=True)
		result = result.stdout.split("\n")[-2].split(" ")[1]
		GlobalEpsilon, NumberFirstPL, NumBlock, NumAtkPL, mice_ratio, mice_scale, elephant_ratio, elephant_scale, times = arg
		outputfile.write(f"{GlobalEpsilon},")
		outputfile.write(f"{NumberFirstPL},")
		outputfile.write(f"{NumBlock},")
		outputfile.write(f"{NumAtkPL},")
		outputfile.write(f"{mice_ratio},")
		outputfile.write(f"{mice_scale},")
		outputfile.write(f"{elephant_ratio},")
		outputfile.write(f"{elephant_scale},")
		outputfile.write(f"{result}\n")
	outputfile.close()
