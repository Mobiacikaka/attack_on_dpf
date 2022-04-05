#!/bin/sh

set -e

onerun() {
	step=$1
	origin_dataset=$(echo "$(cat ./gen.example.arg)" | ./gen2.py)
	poison_dataset=$(echo "$origin_dataset\n$step" | ./attack.py)
	origin_result=$(echo "$origin_dataset" | ./simulation.py)
	poison_result=$(echo "$poison_dataset" | ./simulation.py)
	count_result=$(echo "$poison_dataset\n$poison_result" | ./count.py)
	echo $count_result
}

thousands_run() {
	step=$1
	times=$2
	for i in $(seq 1 $times)
	do
		onerun $step
	done
}

times=10
result_1=$(thousands_run 0.1 $times)
result_2=$(thousands_run 0.2 $times)
result_3=$(thousands_run 0.3 $times)
echo "$times\n$result_1\n$result_2\n$result_3" | ./compare.py
