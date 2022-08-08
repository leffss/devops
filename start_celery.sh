#!/bin/bash

export PYTHONOPTIMIZE=1
/home/python372/bin/celery -A devops worker -l info -c 5 --max-tasks-per-child 200 --prefetch-multiplier 10
