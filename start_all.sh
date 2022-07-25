#!/bin/bash

cd /home/workspace/devops/ && source venv/bin/activate
export PYTHONOPTIMIZE=1

ps_count=$(ps aux|grep -E 'celery|daphne|gunicorn|manage.py'|grep -v grep|wc -l)
if [[ $ps_count != 0 ]];then
  echo 'devops already started, exit 1'
  exit 1
fi

rm -rf logs/*.pid

echo 'start celery worker'
nohup celery -A devops worker -l info -c 3 --max-tasks-per-child 40 --prefetch-multiplier 1 --pidfile logs/celery_worker.pid >> logs/celery_worker.log 2>&1 &

echo 'start celery beat'
nohup celery -A devops beat -l info --pidfile logs/celery_beat.pid >> logs/celery_beat.log 2>&1 &

echo 'start sshd'
nohup python3 manage.py sshd >> logs/sshd.log 2>&1 &

echo 'start daphne'
nohup daphne -b 0.0.0.0 -p 8001 --access-log=logs/daphne_access.log devops.asgi:application >> logs/daphne.log 2>&1 &

echo 'start gunicorn'
nohup gunicorn -c gunicorn.py devops.wsgi:application >> logs/gunicorn.log 2>&1 &
