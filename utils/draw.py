#!/bin/python3

import matplotlib.pyplot as plt
import pandas, numpy

plt.rcParams.update({
    # 'font.family': 'Times New Roman',  # 使用 Times 字体
    'font.size': 18,                   # 设置为 10pt（与正文一致）
    'axes.labelsize': 18,
    'axes.titlesize': 18,
    'xtick.labelsize': 14,
    'ytick.labelsize': 14,
    'legend.fontsize': 12,
    'figure.dpi': 300,                 # 高分辨率图适合打印和论文
    'savefig.dpi': 300,
    'pdf.fonttype': 42,                # 使 PDF 可嵌入文本字体（非路径）
    'ps.fonttype': 42
})

class Result:
	def __init__(self) -> None:
		self.filename:str = ""

	def ReadCsvFile(self, filename: str):
		self.filename = filename
		self.dataframe = pandas.read_csv(self.filename)

	def GetResult(
		self,
		GlobalEpsilon,
		NumberFirstPL,
		NumBlock,
		NumAtkPL,
		mice_ratio,
		mice_scale,
		elephant_ratio,
		elephant_scale,
		result_name,
		mean_or_std,
		_lambda=0.0,
	):
		row = self.dataframe[
			(self.dataframe["GlobalEpsilon"] == GlobalEpsilon) &
			(self.dataframe["NumberFirstPL"] == NumberFirstPL) &
			(self.dataframe["NumBlock"] == NumBlock) &
			(self.dataframe["NumAtkPL"] == NumAtkPL) &
			(self.dataframe["mice_ratio"] == mice_ratio) &
			(self.dataframe["mice_scale"] == mice_scale) &
			(self.dataframe["elephant_ratio"] == elephant_ratio) &
			(self.dataframe["elephant_scale"] == elephant_scale)
		]

		if _lambda != 0.0:
			# row = row[(row["lambda"] == _lambda)]
			row = row[numpy.isclose(_lambda, row["lambda"])]

		try:
			res = row[f"{result_name} {mean_or_std}"].iloc[0]
		except:
			print(locals())
			print(row.head())
			exit()
		return res

class Paintist:
	def __init__(self) -> None:
		self.saveflag = True
		self.showflag = False
		self.scaling_factor = 1000

	def GetResultList(self, attack_name: str, metric_name: str, args: list, result: Result):
		result_list = []
		for arg in args:
			GlobalEpsilon, NumberFirstPL, NumBlock, NumAtkPL, \
				mice_ratio, mice_scale, elephant_ratio, elephant_scale, \
				_lambda = arg
			result_list.append(
				result.GetResult(
					GlobalEpsilon,
					NumberFirstPL,
					NumBlock,
					NumAtkPL,
					mice_ratio,
					mice_scale,
					elephant_ratio,
					elephant_scale,
					attack_name,
					metric_name,
					_lambda,
				)
			)
		return result_list

	def EvaluateK(self):
		result = Result()
		result.ReadCsvFile('../EVALUATION/evaluation_eps.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]

		NumberFirstPL = 100

		mice: tuple = (75, 100)
		elephant: tuple = (25, 1000)
		args = [
			(
				100*1000,
				NumberFirstPL,
				10,
				k_ratio * NumberFirstPL,
				75, 100,  # mice
				25, 1000, # elephant
			)
			for k_ratio in x_list
		]

		def getresultlist(attack_name: str, mice: tuple[int, int], elephant: tuple[int, int]):
			y_list = []
			for i in range(len(x_list)):
				K = int(x_list[i] * 100)
				y_list.append(
					result.GetResult(
						100000,      # GlobalEpsilon
						100,         # NumberFirstPL
						10,          # NumBlock
						K,           # NumAtkPL
						mice[0],     # mice_ratio
						mice[1],     # mice_scale
						elephant[0], # elephant_ratio
						elephant[1], # elephant_scale
						attack_name, # attack method name
						'mean',      # mean or std
					)
				)
			return y_list
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[0].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		mice: tuple = (0, 100)
		elephant: tuple = (100, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[1].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()
		plt.ylim(0.0, 1.0)

		for ax in axes:
			ax.grid()
		fig.supxlabel("K/N")
		fig.supylabel("BCR") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying K.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateN(self):
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list = [50, 100, 150, 200, 250]

		def getresultlist(attack_name: str, mice: tuple[int, float], elephant: tuple[int, float]):
			y_list = []
			for i in range(len(x_list)):
				N = x_list[i]
				K = int(N * 0.3)
				EPS = 1000 * N
				try:
					y_list.append(
						self.result.GetResult(
							EPS,         # GlobalEpsilon
							N,           # NumberFirstPL
							10,          # NumBlock
							K,           # NumAtkPL
							mice[0],     # mice_ratio
							mice[1],     # mice_scale
							elephant[0], # elephant_ratio
							elephant[1], # elephant_scale
							attack_name, # attack method name
							'mean',      # mean or std
						)
					)
				except:
					print(x_list[i])
					exit()
			return y_list

		mice: tuple = (75, 100)
		elephant: tuple = (25, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[0].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		mice: tuple = (0, 100)
		elephant: tuple = (100, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[1].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()
		plt.ylim(0.0, 1.0)

		for ax in axes:
			ax.grid()
		fig.supxlabel("N")
		fig.supylabel("BCR") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying N.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateM(self):
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list = [5, 10, 15, 20, 25, 30]

		def getresultlist(attack_name: str, mice: tuple[int, float], elephant: tuple[int, float]):
			y_list = []
			for i in range(len(x_list)):
				N = 100
				K = int(N * 0.3)
				EPS = 1000 * N
				try:
					y_list.append(
						self.result.GetResult(
							EPS,         # GlobalEpsilon
							N,           # NumberFirstPL
							x_list[i],   # NumBlock
							K,           # NumAtkPL
							mice[0],     # mice_ratio
							mice[1],     # mice_scale
							elephant[0], # elephant_ratio
							elephant[1], # elephant_scale
							attack_name, # attack method name
							'mean',      # mean or std
						)
					)
				except:
					print(x_list[i])
					exit()
			return y_list

		mice: tuple = (75, 100)
		elephant: tuple = (25, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[0].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		mice: tuple = (0, 100)
		elephant: tuple = (100, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[1].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()
		plt.ylim(0.0, 1.0)

		for ax in axes:
			ax.grid()
		fig.supxlabel("M")
		fig.supylabel("BCR") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying M.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateEPS(self):
		# result = Result()
		# result.ReadCsvFile('../EVALUATION/evaluation_eps.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list[float] = [0.5, 0.75, 1.0, 2.0, 3.0]

		# GlobalEpsilon = 100 * self.scaling_factor
		NumberFirstPL = 100
		K = int(NumberFirstPL * 0.3)
		NumBlock = 10

		def getresultlist(attack_name: str, mice: tuple, elephant: tuple, result=self.result):
			y_list = []
			for eps_fs in x_list:
				# NumberFirstPL = int(GlobalEpsilon // eps_fs // self.scaling_factor)
				GlobalEpsilon = self.scaling_factor * eps_fs * NumberFirstPL
				mscale = int(eps_fs * mice[1])
				escale = int(eps_fs * elephant[1])
				y_list.append(
					result.GetResult(
						GlobalEpsilon, NumberFirstPL, NumBlock, K,
						mice[0], mscale,
						elephant[0], escale,
						attack_name, 'mean',
					)
				)
			return y_list

		mice: tuple = (75, self.scaling_factor*0.1)
		elephant: tuple = (25, self.scaling_factor)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[0].plot(range(len(x_list)), y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(range(len(x_list)), y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(range(len(x_list)), y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(range(len(x_list)), y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		mice: tuple = (0, 100)
		elephant: tuple = (100, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[1].plot(range(len(x_list)), y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(range(len(x_list)), y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(range(len(x_list)), y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(range(len(x_list)), y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()
		plt.ylim(0.0, 1.0)

		for ax in axes:
			# ax.set_xscale('log', base=2)
			ax.set_xticks(range(len(x_list)), [str(x) for x in x_list])
			# ax.set_xticklabels([str(x) for x in x_list])
			ax.grid()
		fig.supxlabel(r"$\epsilon^{FS}$")
		fig.supylabel("BCR") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying EPS_FS.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateDefense(self):
		result_defense = Result()
		result_defense.ReadCsvFile('../EVALUATION/evaluation_defense.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]

		NumberFirstPL = 100
		NumBlock = 10
		Epsilon = 1.0
		GlobalEpsilon = int(NumberFirstPL * Epsilon * self.scaling_factor)

		def getresultlist(attack_name: str, mice: tuple, elephant: tuple, result=self.result):
			y_list = []
			for i in range(len(x_list)):
				K = int(x_list[i] * 100)
				y_list.append(
					result.GetResult(
						GlobalEpsilon, NumberFirstPL, NumBlock, K,
						mice[0], mice[1],
						elephant[0], elephant[1],
						attack_name, 'mean',
					)
				)
			return y_list

		mice: tuple = (75, int(self.scaling_factor*0.1))
		elephant: tuple = (25, int(self.scaling_factor))
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('TTA', mice, elephant, result=result_defense)
		y4_list: list = getresultlist('SBFS', mice, elephant, result=result_defense)

		axes[0].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='TTA (w/ Defense)')
		axes[0].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='SBFS (w/ Defense)')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		mice: tuple = (0, int(self.scaling_factor*0.1))
		elephant: tuple = (100, int(self.scaling_factor))
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('TTA', mice, elephant, result=result_defense)
		y4_list: list = getresultlist('SBFS', mice, elephant, result=result_defense)

		axes[1].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='TTA (w/ Defense)')
		axes[1].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='SBFS (w/ Defense)')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()
		plt.ylim(0.0, 1.0)

		for ax in axes:
			ax.grid()
		fig.supxlabel("K/N")
		fig.supylabel("BCR") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying Defense.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateLambda(self):
		result_defense = Result()
		result_defense.ReadCsvFile('../EVALUATION/evaluation_defense.csv')
		fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True, sharey=True)
		x_list: list = [0.1, 0.3, 0.5, 0.7, 0.9]
		x_list: list = numpy.arange(0.9, 1.01, 0.01).tolist()

		NumberFirstPL = 100
		NumBlock = 10
		Epsilon = 1.0
		GlobalEpsilon = int(NumberFirstPL * Epsilon * self.scaling_factor)
		K = 30

		def getresultlist(attack_name: str, mice: tuple, elephant: tuple, result=result_defense):
			y_list = []
			for i in range(len(x_list)):
				y_list.append(
					result.GetResult(
						GlobalEpsilon, NumberFirstPL, NumBlock, K,
						mice[0], mice[1],
						elephant[0], elephant[1],
						attack_name, 'mean',
						x_list[i]
					)
				)
			return y_list

		mice: tuple = (75, 100)
		elephant: tuple = (25, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[0].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		mice: tuple = (0, 100)
		elephant: tuple = (100, 1000)
		y1_list: list = getresultlist('TTA', mice, elephant)
		y2_list: list = getresultlist('SBFS', mice, elephant)
		y3_list: list = getresultlist('Naive', mice, elephant)
		y4_list: list = getresultlist('Random', mice, elephant)

		axes[1].plot(x_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(x_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(x_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(x_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()
		plt.ylim(0.0, 1.0)

		for ax in axes:
			ax.set_xticks(x_list)
			ax.grid()
		fig.supxlabel(r"$\lambda$")
		fig.supylabel("BCR") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying Lambda.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateRuntimeK(self):
		result = Result()
		result.ReadCsvFile('../EVALUATION/evaluation_runtime.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		k_list: list = [10, 20, 30, 40, 50]

		args = [
			(
				100*1000,
				100,
				10,
				K,
				75, 100,
				25, 1000,
				1.0,
			)
			for K in k_list
		]

		y1_list: list = self.GetResultList('TTA',    'time', args, result)
		y2_list: list = self.GetResultList('SBFS',   'time', args, result)
		y3_list: list = self.GetResultList('Naive',  'time', args, result)
		y4_list: list = self.GetResultList('Random', 'time', args, result)

		axes[0].plot(k_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(k_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(k_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(k_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		args = [
			(
				100*1000,
				100,
				10,
				K,
				0, 100,
				100, 1000,
				1.0,
			)
			for K in k_list
		]

		y1_list: list = self.GetResultList('TTA',    'time', args, result)
		y2_list: list = self.GetResultList('SBFS',   'time', args, result)
		y3_list: list = self.GetResultList('Naive',  'time', args, result)
		y4_list: list = self.GetResultList('Random', 'time', args, result)

		axes[1].plot(k_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(k_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(k_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(k_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()

		for ax in axes:
			ax.set_yscale('log')
			ax.grid()
		fig.supxlabel("K")
		fig.supylabel("time (s)") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying Runtime K.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateRuntimeN(self):
		result = Result()
		result.ReadCsvFile('../EVALUATION/evaluation_runtime.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		n_list: list = [50, 100, 150, 200, 250]

		args = [
			(
				N*1000,
				N,
				10,
				10,
				75, 100,
				25, 1000,
				1.0,
			)
			for N in n_list
		]

		y1_list: list = self.GetResultList('TTA',    'time', args, result)
		y2_list: list = self.GetResultList('SBFS',   'time', args, result)
		y3_list: list = self.GetResultList('Naive',  'time', args, result)
		y4_list: list = self.GetResultList('Random', 'time', args, result)

		axes[0].plot(n_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(n_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(n_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(n_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		args = [
			(
				N*1000,
				N,
				10,
				10,
				0, 100,
				100, 1000,
				1.0,
			)
			for N in n_list
		]

		y1_list: list = self.GetResultList('TTA',    'time', args, result)
		y2_list: list = self.GetResultList('SBFS',   'time', args, result)
		y3_list: list = self.GetResultList('Naive',  'time', args, result)
		y4_list: list = self.GetResultList('Random', 'time', args, result)

		axes[1].plot(n_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(n_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(n_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(n_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()

		for ax in axes:
			ax.set_yscale('log')
			ax.grid()
		fig.supxlabel("N")
		fig.supylabel("time (s)") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying Runtime N.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

	def EvaluateRuntimeM(self):
		result = Result()
		result.ReadCsvFile('../EVALUATION/evaluation_runtime.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		m_list = [5, 10, 15, 20, 25]

		args = [
			(
				100*1000,
				100,
				M,
				10,
				75, 100,
				25, 1000,
				1.0,
			)
			for M in m_list
		]

		y1_list: list = self.GetResultList('TTA',    'time', args, result)
		y2_list: list = self.GetResultList('SBFS',   'time', args, result)
		y3_list: list = self.GetResultList('Naive',  'time', args, result)
		y4_list: list = self.GetResultList('Random', 'time', args, result)

		axes[0].plot(m_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[0].plot(m_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[0].plot(m_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[0].plot(m_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[0].set_title("(a) Mice 75%, Elephant 25%")

		args = [
			(
				100*1000,
				100,
				M,
				10,
				0, 100,
				100, 1000,
				1.0,
			)
			for M in m_list
		]

		y1_list: list = self.GetResultList('TTA',    'time', args, result)
		y2_list: list = self.GetResultList('SBFS',   'time', args, result)
		y3_list: list = self.GetResultList('Naive',  'time', args, result)
		y4_list: list = self.GetResultList('Random', 'time', args, result)

		axes[1].plot(m_list, y1_list, marker='s', linestyle='solid', color='green', label='TTA')
		axes[1].plot(m_list, y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
		axes[1].plot(m_list, y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
		axes[1].plot(m_list, y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
		axes[1].set_title("(b) Mice 0%, Elephant 100%")

		plt.xlim()

		for ax in axes:
			ax.set_yscale('log')
			ax.grid()
		fig.supxlabel("M")
		fig.supylabel("time (s)") ## Budget Capture Ratio

		handles, labels = axes[0].get_legend_handles_labels()
		fig.legend(handles, labels,
			loc='lower center',
			bbox_to_anchor=(0.5, 1.02),
			ncol=4,
			frameon=False
		)
		plt.tight_layout()
		if self.saveflag:
			plt.savefig(f"./figs/Varying Runtime M.pdf", bbox_inches='tight')
		if self.showflag:
			plt.show()
		plt.clf()

if __name__ == '__main__':
	p = Paintist()
	# p.EvaluateK()
	# p.EvaluateN()
	# p.EvaluateM()
	# p.EvaluateEPS()
	# p.EvaluateDefense()
	# p.EvaluateLambda()
	# p.EvaluateRuntimeK()
	# p.EvaluateRuntimeN()
	p.EvaluateRuntimeM()
