#!/bin/python
# vim:ts=2:sw=2:noet
def overstep(pl: list, step: float) -> bool:
	for demand in pl:
		if demand > step:
			return True
	return False

def divide_pl(pl: list, step: float) -> tuple:
	new_pl = []
	for i in range(len(pl)):
		tmp = 0
		if pl[i] > step:
			tmp = step
		else:
			tmp = pl[i]
		new_pl.append(tmp)
		pl[i] -= tmp
	return pl, new_pl

def attack(pls: list, attack_no: int=1, step: float=1.0) -> tuple:

	max_pl_no = 0
	if attack_no == 1:
		max_pl_no = 0
	else:
		assert(attack_no == 1)
	
	poison_pl = pls[max_pl_no]
	poison_pls_no = []
	while overstep(poison_pl, step):
		poison_pl, new_pl = divide_pl(poison_pl, step)
		pls.insert(max_pl_no, new_pl)
		poison_pls_no.append(max_pl_no)
		max_pl_no += 1

	if sum(poison_pl) == 0:
		pls.pop(max_pl_no)
	else:
		pls[max_pl_no] = poison_pl
		poison_pls_no.append(max_pl_no)

	return pls, poison_pls_no

eps_Global	= float(input())
first_N		= int(input())
n_prvblck	= int(input())
n_pls		= int(input())

pls = []
for _ in range(n_pls):
	line = input()
	pls.append([float(i) for i in line.split()])

step = float(input())
pls, poison_pls_no = attack(pls, step=step)

print(eps_Global)
print(first_N)
print(n_prvblck)
print(len(pls))
for item in pls:
	for item2 in item:
		print('%.4f'%item2, end=" ")
	print()

for pl_no in poison_pls_no:
	print(pl_no, end=" ")
print()
