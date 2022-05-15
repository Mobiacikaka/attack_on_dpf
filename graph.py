#!/bin/python
# vim:ts=2:sw=2:noet

import matplotlib.pyplot as plt
import numpy as np

def laplace(eps: float) -> float:
	if eps == 0:
		return 0
	return np.random.laplace(loc=0, scale=1/eps)

def dandc(eps: float, n: int) -> float:
	s = 0
	for _ in range(n):
		s += laplace(eps / n)
	return s / n

def subandc(eps: float, eps1: float) -> float:
	s = 0
	s += laplace(eps - eps1) * (eps - eps1) / eps
	s += laplace(eps1) * eps1 / eps
	return s

def listlaplace(eps_list: list[float]) -> float:
	s = 0
	eps_total = sum(eps_list)
	for eps in eps_list:
		s += laplace(eps) * eps / eps_total
	return s

def draw():
	eps1 = [1.0, 1.0, 1.0]
	eps2 = [2.8]
	x1 = []
	x2 = []

	for _ in range(100000):
		x1.append(listlaplace(eps1))
		x2.append(listlaplace(eps2))

	rng = (-4, 4)
	plt.hist(x1, bins=100, edgecolor='None', alpha=0.5, color='r', range=rng)
	plt.hist(x2, bins=100, edgecolor='None', alpha=0.5, color='b', range=rng)
	plt.title("red: "+str(eps1) + "\n blue: "+str(eps2))
	plt.show()

	rng = 0.1
	s1 = 0
	s2 = 0
	for i in x1:
		s1 += i > -rng and i < rng
	for i in x2:
		s2 += i > -rng and i < rng
	print(s1, s2)


def draw2():
	eps_list = []
	eps_list.append([1.0, 1.0, 1.0])
	eps_list.append([2.8])
	eps_list.append([3.0])

	title = ""
	for eps in eps_list:
		x = []
		title += "\n" + str(eps)
		for _ in range(100000):
			x.append(listlaplace(eps))

		rng = (-2, 2)
		plt.hist(x, bins=100, edgecolor="None", alpha=0.5, range=rng)

		s = 0
		rng = 0.1
		for xi in x:
			s += xi > -rng and xi < rng
		print(s)

	plt.title(title)
	plt.show()
	
draw()
