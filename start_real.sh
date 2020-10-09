
cd /home/workspace/devops/ && /home/python372/bin/pip3 install -i https://mirrors.aliyun.com/pypi/simple -r requirements.txt

cd /home/workspace/devops/ && export PYTHONOPTIMIZE=1 && /home/python372/bin/celery -A devops worker -l info -c 3 --max-tasks-per-child 40 --prefetch-multiplier 1 --pidfile logs/celery_worker.pid

cd /home/workspace/devops/ && export PYTHONOPTIMIZE=1 && /home/python372/bin/celery -A devops beat -l info --pidfile logs/celery_beat.pid

cd /home/workspace/devops/ && export PYTHONOPTIMIZE=1 && /home/python372/bin/python3 manage.py sshd

cd /home/workspace/devops/ && export PYTHONOPTIMIZE=1 && /home/python372/bin/daphne -b 0.0.0.0 -p 8001 devops.asgi:application

cd /home/workspace/devops/ && export PYTHONOPTIMIZE=1 && /home/python372/bin/gunicorn -c gunicorn.py devops.wsgi:application
