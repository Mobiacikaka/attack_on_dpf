import subprocess

def getresult(target_attack: str, lines: list[str]):
	for i in range(len(lines)):
		if target_attack in lines[i]:
			result = lines[i].split(":")[1]
			mean = result.split(" ")[1]
			std = result.split(" ")[2]
			return mean, std
	assert(0)
	return "", ""

def ensure_clean():
	dirty = subprocess.check_output(
		["git", "status", "--porcelain"]
	).decode().strip()
	if dirty:
		raise RuntimeError("Working tree is dirty. Please commit or stash.")

def run():
	dirty = subprocess.check_output(
		["git", "status", "--porcelain"]
	).decode().strip()
	if dirty:
		print("PLEASE COMMIT FIRST")
		exit()

	scaling_factor = 1000
	args = [
		(
			int(step * NumberFirstPL * scaling_factor),
			NumberFirstPL,
			NumBlock,
			int(K_ratio * NumberFirstPL), ## Number of AtkPipeline
			mice_ratio,
			int(mice_scale * step * scaling_factor),
			elephant_ratio,
			int(elephant_scale * step * scaling_factor),
			times
		)
		for NumberFirstPL, step in [(40, 3), (60, 2), (120, 1), (160, 0.75), (240, 0.5)] #[(50, 2), (100, 1), (200, 0.5), (400, 0.25)]
		# for step in [1.0]
		for NumBlock in [10]# range(5, 31, 5)
		# for NumberFirstPL in [100]# range(50, 251, 50)
		for K_ratio in [0.1, 0.2, 0.3, 0.4, 0.5]
		for mice_scale in [0.1]
		for elephant_scale in [1.0]
		for mice_ratio, elephant_ratio in [(75, 25), (0, 100)]
		for times in [100]
	]

	outputfile = open("../EVALUATION/evaluation_defense.csv", "w")
	column_list = [
		"GlobalEpsilon,"
		,"NumberFirstPL,"
		,"NumBlock,"
		,"NumAtkPL,"
		,"mice_ratio,"
		,"mice_scale,"
		,"elephant_ratio,"
		,"elephant_scale,"
		,"TTA mean,"
		,"TTA std,"
		,"SBFS mean,"
		,"SBFS std,"
		,"Naive mean,"
		,"Naive std,"
		,"Random mean,"
		,"Random std"
	]
	header = ""
	for column_name in column_list:
		header += column_name
	outputfile.write(f"{header}\n")
	i = 1
	for arg in args:
		input_str = ""
		for par in arg:
			input_str = input_str + f"{par}\n"

		print(f"Running {i} args")
		i += 1
		print(input_str)

		ensure_clean()
		output = subprocess.run(
			["python", "main.py"], input=input_str, capture_output=True, text=True,
		)
		# result = result.stdout.split("\n")[-2].split(" ")[1]
		result_1: tuple[str, str] = getresult("Threshold", output.stdout.split("\n"))
		result_2: tuple[str, str] = getresult("Segmented", output.stdout.split("\n"))
		result_3: tuple[str, str] = getresult("Naive", output.stdout.split("\n"))
		result_4: tuple[str, str] = getresult("Random", output.stdout.split("\n"))
		GlobalEpsilon, NumberFirstPL, NumBlock, NumAtkPL, mice_ratio, mice_scale, elephant_ratio, elephant_scale, times = arg
		outputfile.write(f"{GlobalEpsilon},")
		outputfile.write(f"{NumberFirstPL},")
		outputfile.write(f"{NumBlock},")
		outputfile.write(f"{NumAtkPL},")
		outputfile.write(f"{mice_ratio},")
		outputfile.write(f"{mice_scale},")
		outputfile.write(f"{elephant_ratio},")
		outputfile.write(f"{elephant_scale},")
		outputfile.write(f"{result_1[0]},")
		outputfile.write(f"{result_1[1]},")
		outputfile.write(f"{result_2[0]},")
		outputfile.write(f"{result_2[1]},")
		outputfile.write(f"{result_3[0]},")
		outputfile.write(f"{result_3[1]},")
		outputfile.write(f"{result_4[0]},")
		outputfile.write(f"{result_4[1]}\n")
	outputfile.close()
