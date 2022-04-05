#!/bin/python3
# vim:ts=2:sw=2:noet

from dpf import Simulation

eps_Global = float(input())
first_NPL = int(input())
NPB = int(input())
NPL = int(input())
pls = []
for _ in range(NPL):
	line = input()
	pls.append([float(item) for item in line.split()])

alloc_pls = Simulation(eps_Global, first_NPL, NPB, pls)
for i in range(NPL):
	if i not in alloc_pls:
		print(i, end=" ")
print()
