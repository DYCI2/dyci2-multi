#!/bin/sh

repo=$1

for file in $repo
do 
	python ./src/oracle/errgen.py $file
done
