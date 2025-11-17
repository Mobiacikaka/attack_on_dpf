#!/bin/python3

import matplotlib.pyplot as plt

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

def DrawK():
	"""
	M=10, N=100, epsilon=100.0, (step=1.0)
	mice_ratio=0.75, mice_scale=0.1
	elephant_ratio=0.25, elephant_scale=1.0
	"""

	M, N, E, MR, MS, ER, ES = 10, 100, 100, 75, 10, 25, 100
	X_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]
	## LBA
	Y1_list: list = [0.5710986, 0.6345638, 0.6882172, 0.7393076, 0.7824966]
	Y1_list: list = [0.5955706, 0.6566713, 0.7191044, 0.7726532, 0.8177798]
	## DSA
	Y2_list: list = [0.7004834, 0.7442992, 0.8058750, 0.8576998, 0.8862787]
	## GREEDY
	Y3_list: list = [0.539633 , 0.4062988, 0.6096552, 0.7069462, 0.7374655]
	## RANDOM
	Y4_list: list = [0.0311414, 0.0645959, 0.1010515, 0.1373639, 0.1683657]

	"""
	M=10, N=100, epsilon=100.0, (step=1.0)
	mice_ratio=100, mice_scale=10
	elephant_ratio=0, elephant_scale=100

	M, N, E, MR, MS, ER, ES = 10, 100, 100, 100, 10, 0, 100
	X_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]
	## LBA
	Y1_list: list = [0.1000000, 0.2000000, 0.3009531, 0.4087082, 0.5446099]
	## DSA
	Y2_list: list = [0.3011267, 0.5465031, 0.7373412, 0.8678937, 0.9386852]
	## GREEDY
	Y3_list: list = [0.1284858, 0.1740471, 0.2594669, 0.3544396, 0.4600593]
	## RANDOM
	Y4_list: list = [0.0912589, 0.1854378, 0.2754931, 0.3687428, 0.4616255]
	"""

	plt.plot(X_list, Y1_list, marker='s', linestyle='solid', color='green', label='LBA')
	plt.plot(X_list, Y2_list, marker='^', linestyle='-.', color='red', label='DSA')
	plt.plot(X_list, Y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
	plt.plot(X_list, Y4_list, marker='v', linestyle='dotted',  color='black', label='Random')

	plt.xlim()
	plt.ylim(0.0, 1.0)
	plt.xlabel("K/N")
	plt.ylabel("BCR") ## Budget Capture Ratio
	plt.grid(); plt.legend(); plt.tight_layout();
	# plt.savefig(f"figs/M{M}_N{N}_E{E}_MR{MR}_MS{MS}_ER{ER}_ES{ES}.eps", bbox_inches='tight')
	plt.show()
	plt.clf()

def DrawM():
	"""
	K=30
	mice ratio 75
	elephant ratio 25
	"""
	K, N, E, MR, MS, ER, ES = 30, 100, 100, 75, 10, 25, 100
	X_list: list = [5, 10, 15, 20, 25, 30]
	## LBA
	Y1_list: list = [0.707739 , 0.6882172, 0.67738930, 0.6703677 , 0.6622754 , 0.66430970]
	## DSA
	Y2_list: list = [0.7853968, 0.805875 , 0.82686611, 0.83651105, 0.85351504, 0.85924037]
	## GREEDY
	Y3_list: list = [0.6107828, 0.6096552, 0.61547754, 0.6185876 , 0.61370484, 0.62097277]
	## RANDOM
	Y4_list: list = [0.0990902, 0.1010515, 0.09968501, 0.09889975, 0.10119952, 0.10185223]

	plt.plot(X_list, Y1_list, marker='s', linestyle='solid', color='green', label='LBA')
	plt.plot(X_list, Y2_list, marker='^', linestyle='-.', color='red', label='DSA')
	plt.plot(X_list, Y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
	plt.plot(X_list, Y4_list, marker='v', linestyle='dotted',  color='black', label='Random')

	plt.xlim()
	plt.ylim(0.0, 1.0)
	plt.xlabel("M")
	plt.ylabel("BCR") ## Budget Capture Ratio
	plt.grid(); plt.legend(loc='center right'); plt.tight_layout();
	# plt.savefig(f"figs/K{K}_N{N}_E{E}_MR{MR}_MS{MS}_ER{ER}_ES{ES}.eps", bbox_inches='tight')
	plt.show()
	plt.clf()

if __name__ == '__main__':
	DrawK()
