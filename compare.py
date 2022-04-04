#!/bin/python
# vim:ts=2:sw=2:noet

import numpy as np

times=int(input())

result_1 = []
for i in range(times):
	result_1.append(float(input()))
result_2 = []
for i in range(times):
	result_2.append(float(input()))
result_3 = []
for i in range(times):
	result_3.append(float(input()))

print(np.var(result_1))
print(np.var(result_2))
print(np.var(result_3))
