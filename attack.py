#!/bin/python
# vim:ts=2:sw=2:noet

from K_attack import k_attack

def main():
	eps_Global= float(input())
	first_NPL	= int(input())
	NPB	= int(input())

	NPL	= int(input())
	normal_pls = []
	for _ in range(NPL):
		normal_pls.append([float(i) for i in input().split()])

	poison_num = int(input())
	poison_pls = []
	for _ in range(poison_num):
		poison_pls.append([float(i) for i in input().split()])

	# step = float(input())
	sim_arg = (eps_Global, first_NPL, NPB, normal_pls, poison_pls)
	pls, poison_pls_no = k_attack(5, sim_arg)

	print(eps_Global)
	print(first_NPL)
	print(NPB)
	print(len(pls))
	for item in pls:
		for item2 in item:
			print('%.4f'%item2, end=" ")
		print()

	for pl_no in poison_pls_no:
		print(pl_no, end=" ")
	print()

main()
