#!/bin/python
# vim:ts=2:sw=2:noet

from itertools import combinations
import numpy as np

def gen_2dim_array(n: int, m: int) -> list:
	# generate 2-dimentional array
	arr = []
	for _ in range(n):
		row = []
		for _ in range(m):
			row.append(np.random.randint(1, 100))
		arr.append(row)
	return arr

def colmax(arr: list[list], k: int, m: int) -> list:
	collist = []
	for j in range(m):
		maxv = 0
		for i in range(k):
			if maxv < arr[i][j]:
				maxv = arr[i][j]
		collist.append(maxv)
	return collist

def brute_force(arr: list[list], n: int, m: int, k: int) -> list:
	maxm = 0
	maxrlist = []
	for rowlist in combinations(list(range(n)), k):
		rowlist = list(rowlist)
		rows = []
		for rid in rowlist:
			rows.append(arr[rid])
		colm = sum(colmax(rows, k, m))
		if colm > maxm:
			maxrlist = rowlist
			maxm = colm
	return maxrlist

def greedy(arr: list[list], n: int, m: int, k: int) -> list:
	maxvdict = {}
	for i in range(n):
		maxvdict[i] = [0]
	for j in range(m):
		maxv = 0
		maxvindex = -1
		for i in range(n):
			if maxv < arr[i][j]:
				maxv = arr[i][j]
				maxvindex = i
		maxvdict[maxvindex].append(maxv)
	rowlist = sorted(maxvdict, key=lambda x: sum(maxvdict.get(x)), reverse=True)
	rowlist = sorted(rowlist[:k])
	return rowlist

def dp(arr: list[list], n: int, m: int, k: int) -> list:
	return []

def sum_maxv(arr, rowlist, n, m, k):
	rows = []
	for rid in rowlist:
		rows.append(arr[rid])
	return sum(colmax(rows, k, m))

def greedy_switch(arr: list[list], n: int, m: int, k: int) -> list:
	rowlist = greedy(arr, n, m, k)
	maxv = sum_maxv(arr, rowlist, n, m, k)

	from copy import deepcopy

	while True:
		for i in range(len(rowlist)):
			for rid in range(n):
				if rid not in rowlist:
					newlist = deepcopy(rowlist)
					newlist[i] = rid
					newmaxv = sum_maxv(arr, newlist, n, m, k)
					if newmaxv > maxv:
						rowlist = newlist
						maxv = newmaxv

	# while True:
	# 	tmp_rlist = deepcopy(rowlist)
	# 	tmp_maxv = maxv
	# 	for i in range(len(rowlist)):
	# 		for rid in range(n):
	# 			if rid not in tmp_rlist:
	# 				new_rlist = deepcopy(rowlist)
	# 				new_rlist[i] = rid
	# 				new_v = sum_maxv(arr, new_rlist, n, m, k)
	# 				if new_v > tmp_maxv:
	# 					tmp_maxv = new_v
	# 					tmp_rlist = deepcopy(new_rlist)
		
	# 	if tmp_maxv == maxv:
	# 		break
	# 	elif tmp_maxv > maxv:
	# 		rowlist = deepcopy(tmp_rlist)
	# 		maxv = tmp_maxv

	return sorted(rowlist)

if __name__ == '__main__':
	n = 20
	m = 15
	k = 5
	dataset = gen_2dim_array(n, m)
	# for e in dataset:
	# 	print(e)
	# print()

	def callfunc(funcname, name):
		rlist = funcname(dataset, n, m, k)
		maxv = sum_maxv(dataset, rlist, n, m, k)
		print(f'{name} : {rlist}, sum: {maxv}')

	callfunc(brute_force, 'brute')
	callfunc(greedy, 'greedy')
	callfunc(greedy_switch, 'greedy_switch')
