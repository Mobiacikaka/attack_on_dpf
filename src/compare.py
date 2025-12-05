import csv, os

def getresult(filename: str):
    last_elements = []
    with open(filename) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row:
                last_elements.append(row[-1])
    return last_elements

files = ["../EVALUATION/"+f for f in os.listdir('../EVALUATION') if f.startswith('result_')]
files.sort()

if not files:
	print("No result files.")
	exit()

print("Result Files:")
for idx, f in enumerate(files):
	print(f"{idx}: {f}")

try:
    i, j = map(int, input("Enter two numbers (split with space): ").split())
except ValueError:
    print("Input format error.")
    exit()

if not (0 <= i < len(files) and 0 <= j < len(files)):
    print("Input out of range.")
    exit()

result1 = getresult(files[i])
result2 = getresult(files[j])

if not len(result1) == len(result2):
	print("Different result length.")
	exit()

c1 = 0
c2 = 0
GAMMA = 0.01
for k in range(1, len(result1)):
	if float(result1[k]) - float(result2[k]) > GAMMA:
		c1 += 1
	if float(result2[k]) - float(result1[k]) > GAMMA:
		c2 += 1

print(f"{files[i]} > ({GAMMA}) {files[j]}:\n", c1)
print(f"{files[j]} > ({GAMMA}) {files[i]}:\n", c2)
