#!/bin/python
# vim:ts=2:sw=2:noet

from itertools import combinations
import numpy as np

## Assist Function
# generate 2-dimentional array
def gen_2dim_array(n: int, m: int) -> list:
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
		for i in range(len(arr)):
			if maxv < arr[i][j]:
				maxv = arr[i][j]
		collist.append(maxv)
	return collist

def sum_maxv(arr: list[list[int|float]], rowlist: list[int], n: int, m: int, k: int) -> int|float:
	rows = []
	for rid in rowlist:
		rows.append(arr[rid])
	return sum(colmax(rows, k, m))


## Main Choosen Function
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
	dp_r = []

	for _ in range(n):
		dp_r.append([])

	for _ in range(k):
		new_r = []
		for i in range(n):
			pivot_id = -1
			pivot_m = sum_maxv(arr, dp_r[i], n, m, k)
			for j in range(n):
				tmp_r = dp_r[j] + [i]
				tmp_m = sum_maxv(arr, tmp_r, n, m, k)
				if tmp_m > pivot_m:
					pivot_id = j
					pivot_m = tmp_m
			if pivot_id >= 0:
				new_r.append(dp_r[pivot_id] + [i])
			else:
				new_r.append(dp_r[i])

		dp_r = new_r

	maxid = 0
	for i in range(1, n):
		if sum_maxv(arr, dp_r[i], n, m, k) > sum_maxv(arr, dp_r[maxid], n, m, k):
			maxid = i
	
	max_r = dp_r[maxid]
	sorted(max_r)
	return max_r


## Repair Function
def repair(arr: list[list], n: int, m: int, k: int, rowlist: list[int]) -> list:
	maxv = sum_maxv(arr, rowlist, n, m, k)

	from copy import deepcopy

	while True:
		old_maxv = maxv
		for i in range(len(rowlist)):
			for rid in range(n):
				if rid not in rowlist:
					newlist = deepcopy(rowlist)
					newlist[i] = rid
					newmaxv = sum_maxv(arr, newlist, n, m, k)
					if newmaxv > maxv:
						rowlist = newlist
						maxv = newmaxv
		if maxv == old_maxv:
			break

	return sorted(rowlist)


