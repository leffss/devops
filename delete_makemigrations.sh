#!/bin/bash

cd apps

lists=$(ls)
for i in $lists;do
	rm -f $i/migrations/000*.py
done

