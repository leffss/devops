#!/bin/bash

cd apps

lists=$(ls)
for i in $lists;do
	ls -d $i/migrations/* | grep -v '__init__.py' | xargs rm -rf
done
