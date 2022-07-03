#!/bin/python
# vim:ts=2:sw=2:noet

if __name__ == '__main__':
	eps_Global = float(input())
	first_NPL = int(input())
	NPB = int(input()) # number of data block

	NPL = int(input())
	benign_pls = []
	for _ in range(NPL):
		benign_pls.append([float(i) for i in input().split()])

	sim_arg = (eps_Global, first_NPL, NPB, benign_pls)
