import subprocess, numpy

def getresult(target_attack: str, lines: list[str]):
	for i in range(len(lines)):
		if target_attack in lines[i]:
			result = lines[i].split(":")[1]
			result_line = result.split(" ")[1:]
			return result_line
	assert(0)
	return ["", "", ""]

def ensure_clean():
	dirty = subprocess.check_output(
		["git", "status", "--porcelain"]
	).decode().strip()
	if dirty:
		raise RuntimeError("Working tree is dirty. Please commit or stash.")

def run():
	scaling_factor = 1000
	args = [
		(
			int(step * NumberFirstPL * scaling_factor),
			NumberFirstPL,
			NumBlock,
			int(K_ratio * NumberFirstPL), ## Number of AtkPipeline
			# K,
			mice_ratio,
			int(mice_scale * step * scaling_factor),
			elephant_ratio,
			int(elephant_scale * step * scaling_factor),
			times,
			_lambda
		)
		# for NumberFirstPL, step in [(50, 2), (100, 1), (200, 0.5), (400, 0.25)]
		for step in [0.5, 0.75, 1.0, 2.0, 3.0]
		for NumBlock in range(5, 31, 5)
		for NumberFirstPL in range(50, 251, 50)
		for K_ratio in [0.1, 0.2, 0.3, 0.4, 0.5]
		# for K in [10, 20, 30, 40, 50]
		for mice_scale in [0.1]
		for elephant_scale in [1.0]
		for mice_ratio, elephant_ratio in [(75, 25), (0, 100)]
		for times in [100]
		for _lambda in [1.0]# [0.5, 0.7] + numpy.arange(0.9, 1.01, 0.01).tolist()
	]

	outputfile = open("../EVALUATION/evaluation.csv", "w")
	column_list = [
		"GlobalEpsilon,"
		,"NumberFirstPL,"
		,"NumBlock,"
		,"NumAtkPL,"
		,"mice_ratio,"
		,"mice_scale,"
		,"elephant_ratio,"
		,"elephant_scale,"
		,"lambda,"
		,"TTA mean,"
		,"TTA std,"
		,"TTA time,"
		,"SBFS mean,"
		,"SBFS std,"
		,"SBFS time,"
		,"Naive mean,"
		,"Naive std,"
		,"Naive time,"
		,"Random mean,"
		,"Random std,"
		,"Random time,"
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

		print(f"Running {i}/{len(args)} args")
		i += 1
		print(input_str)

		# ensure_clean()
		output = subprocess.run(
			["python", "main.py"], input=input_str, capture_output=True, text=True,
		)
		# result = result.stdout.split("\n")[-2].split(" ")[1]
		method_names = ["Threshold", "Segmented", "Naive", "Random"]
		result_list: list[list] = []
		for j in range(len(method_names)):
			result_list.append(getresult(method_names[j], output.stdout.split("\n")))
		GlobalEpsilon, NumberFirstPL, NumBlock, NumAtkPL, mice_ratio, mice_scale, elephant_ratio, elephant_scale, times, _lambda = arg
		outputfile.write(f"{GlobalEpsilon},")
		outputfile.write(f"{NumberFirstPL},")
		outputfile.write(f"{NumBlock},")
		outputfile.write(f"{NumAtkPL},")
		outputfile.write(f"{mice_ratio},")
		outputfile.write(f"{mice_scale},")
		outputfile.write(f"{elephant_ratio},")
		outputfile.write(f"{elephant_scale},")
		outputfile.write(f"{_lambda},")
		for result in result_list:
			for item in result:
				outputfile.write(f"{item},")
		outputfile.write("\n")
	outputfile.close()
