#!/bin/python3

import matplotlib.pyplot as plt
import pandas

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

		return row[f"{result_name} {mean_or_std}"].iloc[0]

def DrawM():
	fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)

	"""
	K=30, E(epsilon)
	mice ratio 75
	elephant ratio 25
	"""
	K, N, E, MR, MS, ER, ES = 30, 100, 100, 75, 10, 25, 100
	X_list: list = [5, 10, 15, 20, 25, 30]
	## TTA
	Y1_list: list = [0.758102 , 0.747979 , 0.749895  , 0.752334  , 0.746631  , 0.753732  ]
	## SBFS
	Y2_list: list = [0.8292128, 0.8510804, 0.86946882, 0.8828019 , 0.89529508, 0.90321666]
	## GREEDY
	Y3_list: list = [0.6107828, 0.6096552, 0.61547754, 0.6185876 , 0.61370484, 0.62097277]
	## RANDOM
	Y4_list: list = [0.0990902, 0.1010515, 0.09968501, 0.09889975, 0.10119952, 0.10185223]

	axes[0].plot(X_list, Y1_list, marker='s', linestyle='solid', color='green', label='TTA')
	axes[0].plot(X_list, Y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
	axes[0].plot(X_list, Y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
	axes[0].plot(X_list, Y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
	axes[0].set_title("Mice 75%, Elephant 25%")

	"""
	K=30, E(epsilon)
	mice ratio 75
	elephant ratio 25
	"""

	K, N, E, MR, MS, ER, ES = 30, 100, 100, 0, 10, 100, 100
	X_list: list = [5, 10, 15, 20, 25, 30]
	## TTA
	Y1_list: list = [0.417298 , 0.440892 , 0.458123  , 0.475198 , 0.489821  , 0.497435  ]
	## SBFS
	Y2_list: list = [0.6539794, 0.7218023, 0.76990457, 0.8031399, 0.83788032, 0.86150137]
	## GREEDY
	Y3_list: list = [0.2744416, 0.2594669, 0.25728815, 0.2546375, 0.25363964, 0.24548976]
	## RANDOM
	Y4_list: list = [0.2803764, 0.2754931, 0.27446752, 0.2703381, 0.26739816, 0.26450936]

	axes[1].plot(X_list, Y1_list, marker='s', linestyle='solid', color='green', label='TTA')
	axes[1].plot(X_list, Y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
	axes[1].plot(X_list, Y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
	axes[1].plot(X_list, Y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
	axes[1].set_title("Mice 0%, Elephant 100%")

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
	plt.savefig(f"figs/Varying M.pdf", bbox_inches='tight')
	# plt.show()
	plt.clf()

class Paintist:
	def __init__(self, filename: str) -> None:
		self.result = Result()
		self.result.ReadCsvFile(filename)
		self.saveflag = True
		self.showflag = False

	def EvaluateK(self):
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]

		def getresultlist(attack_name: str, mice: tuple[int, int], elephant: tuple[int, int]):
			y_list = []
			for i in range(len(x_list)):
				K = int(x_list[i] * 100)
				y_list.append(
					self.result.GetResult(
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
		axes[0].set_title("Mice 75%, Elephant 25%")

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
		axes[1].set_title("Mice 0%, Elephant 100%")

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
		axes[0].set_title("Mice 75%, Elephant 25%")

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
		axes[1].set_title("Mice 0%, Elephant 100%")

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
		axes[0].set_title("Mice 75%, Elephant 25%")

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
		axes[1].set_title("Mice 0%, Elephant 100%")

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

if __name__ == '__main__':
	p = Paintist('../EVALUATION/evaluation.csv')
	p.EvaluateK()
	p.EvaluateN()
	p.EvaluateM()
