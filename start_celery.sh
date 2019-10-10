#!/bin/bash

export PYTHONOPTIMIZE=1
/home/python372/bin/celery -A devops worker -l info -c 3 --max-tasks-per-child 40 --prefetch-multiplier 1
