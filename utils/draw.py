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

		try:
			res = row[f"{result_name} {mean_or_std}"].iloc[0]
		except:
			print(locals())
			print(row.head())
			exit()
		return res

class Paintist:
	def __init__(self, filename: str) -> None:
		self.result = Result()
		self.result.ReadCsvFile(filename)
		self.saveflag = True
		self.showflag = True
		self.scaling_factor = 1000

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

	def EvaluateEPS(self):
		result = Result()
		result.ReadCsvFile('../EVALUATION/evaluation_eps.csv')
		fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)
		x_list: list[float] = [0.5, 1.0, 2.0, 3.0]

		def getresultlist(attack_name: str, mice: tuple, elephant: tuple):
			y_list = []
			for eps_fs in x_list:
				N = 100
				eps_g = int(eps_fs * N * 1000)
				K = int(0.3 * N)
				mscale = int(eps_fs * mice[1])
				escale = int(eps_fs * elephant[1])
				y_list.append(
					self.result.GetResult(
						eps_g,       # GlobalEpsilon
						N,           # NumberFirstPL
						10,          # NumBlock
						K,           # NumAtkPL
						mice[0],     # mice_ratio
						mscale,      # mice_scale
						elephant[0], # elephant_ratio
						escale,      # elephant_scale
						attack_name, # attack method name
						'mean',      # mean or std
					)
				)
			return y_list

		mice: tuple = (75, self.scaling_factor*0.1)
		elephant: tuple = (25, self.scaling_factor)
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


if __name__ == '__main__':
	p = Paintist('../EVALUATION/evaluation.csv')
	# p.EvaluateK()
	# p.EvaluateN()
	# p.EvaluateM()
	p.EvaluateEPS()
