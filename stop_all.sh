#!/bin/bash

cd /home/workspace/devops/ && source venv/bin/activate

ps_count=$(ps aux|grep -E 'celery|daphne|gunicorn|manage.py'|grep -v grep|wc -l)
if [[ $ps_count == 0 ]];then
  echo 'devops already stopped, exit 1'
  exit 1
fi

echo 'stop daphne'
ps aux|grep daphne|grep -v grep|awk '{print $2}'|xargs kill

echo 'stop gunicorn'
ps aux|grep gunicorn|grep -v grep|awk '{print $2}'|xargs kill

echo 'stop sshd'
ps aux|grep sshd|grep manage.py|awk '{print $2}'|xargs kill

echo 'stop celery worker and beat'
ps aux|grep celery|grep -E 'worker|beat'|awk '{print $2}'|xargs kill
