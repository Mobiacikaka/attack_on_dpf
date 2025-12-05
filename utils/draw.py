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
	fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)

	"""
	M=10, N=100, epsilon=100.0, (step=1.0)
	mice_ratio=75, mice_scale=0.1
	elephant_ratio=25, elephant_scale=1.0
	"""
	M, N, E, MR, MS, ER, ES = 10, 100, 100, 75, 10, 25, 100
	X_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]
	## TTA
	Y1_list: list = [0.58811  , 0.6755760, 0.747979 , 0.808875 , 0.855238 ]
	## SBFS
	Y2_list: list = [0.7004834, 0.7442992, 0.8058750, 0.8576998, 0.8862787]
	## Naive Greedy
	Y3_list: list = [0.539633 , 0.4062988, 0.6096552, 0.7069462, 0.7374655]
	## Random
	Y4_list: list = [0.0311414, 0.0645959, 0.1010515, 0.1373639, 0.1683657]

	axes[0].plot(X_list, Y1_list, marker='s', linestyle='solid', color='green', label='TTA')
	axes[0].plot(X_list, Y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
	axes[0].plot(X_list, Y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
	axes[0].plot(X_list, Y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
	axes[0].set_title("Mice 75%, Elephant 25%")

	"""
	M=10, N=100, epsilon=100.0, (step=1.0)
	mice_ratio=100, mice_scale=10
	elephant_ratio=0, elephant_scale=100
	"""

	M, N, E, MR, MS, ER, ES = 10, 100, 100, 100, 10, 0, 100
	X_list: list = [0.1, 0.2, 0.3, 0.4, 0.5]
	## TTA
	Y1_list: list = [0.143893 , 0.3019400, 0.440892 , 0.568318 , 0.6956540]
	## SBFS
	Y2_list: list = [0.3011267, 0.5465031, 0.7373412, 0.8678937, 0.9386852]
	## GREEDY
	Y3_list: list = [0.1284858, 0.1740471, 0.2594669, 0.3544396, 0.4600593]
	## RANDOM
	Y4_list: list = [0.0912589, 0.1854378, 0.2754931, 0.3687428, 0.4616255]

	axes[1].plot(X_list, Y1_list, marker='s', linestyle='solid', color='green', label='TTA')
	axes[1].plot(X_list, Y2_list, marker='^', linestyle='-.', color='red', label='SBFS')
	axes[1].plot(X_list, Y3_list, marker='o', linestyle='-.', color='blue', label='Naive Greedy')
	axes[1].plot(X_list, Y4_list, marker='v', linestyle='dotted',  color='black', label='Random')
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
	plt.savefig(f"./figs/Varying K.pdf", bbox_inches='tight')
	# plt.show()
	plt.clf()

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

def DrawN():
	fig, axes = plt.subplots(1, 2, figsize=(10, 4), sharex=True, sharey=True)

	"""
	K=30, E(epsilon)
	mice ratio 75
	elephant ratio 25
	"""
	K, M, E, MR, MS, ER, ES = 0.3, 10, 100, 75, 10, 25, 100
	X_list: list = [50, 100, 150, 200, 250]
	## TTA
	Y1_list: list = [0.743842, 0.747979, 0.7572273, 0.760004, 0.7621608]
	## SBFS
	Y2_list: list = [0.8485134, 0.8510804, 0.851185, 0.84685035, 0.84671528]
	## GREEDY
	Y3_list: list = [0.655906, 0.6096552, 0.60798547, 0.59823375, 0.59255144]
	## RANDOM
	Y4_list: list = [0.1016874, 0.1010515, 0.09801714, 0.100626, 0.10105096]

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
	X_list: list = [50, 100, 150, 200, 250]
	## TTA
	Y1_list: list = [0.44422, 0.440892, 0.4335847, 0.429692, 0.4237032]
	## SBFS
	Y2_list: list = [0.7297192, 0.7218023, 0.71315606, 0.70753995, 0.70487884]
	## GREEDY
	Y3_list: list = [0.2886086, 0.2594669, 0.25968613, 0.27144265, 0.26923692]
	## RANDOM
	Y4_list: list = [0.2675436, 0.2754931, 0.28049146, 0.28543515, 0.28869192]

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
	plt.savefig(f"figs/Varying N.pdf", bbox_inches='tight')
	# plt.show()
	plt.clf()

if __name__ == '__main__':
	DrawM()
