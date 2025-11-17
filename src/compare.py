import csv

def getresult(filename: str):
    last_elements = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                last_elements.append(row[-1])
    return last_elements

baseline = getresult('./result_lba.csv')
# result = getresult('./result_lba_median.csv')
# result = getresult('./result_minplusstep.csv')
result = getresult('./result_MinPlusStep.bak.csv')

c1 = 0
c2 = 0
GAMMA = 0.001
for i in range(1, len(baseline)):
	if float(result[i]) - float(baseline[i]) > GAMMA:
		c1 += 1
	if float(baseline[i]) - float(result[i]) > GAMMA:
		c2 += 1

print(c1, c2)
