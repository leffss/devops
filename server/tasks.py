from devops.celery import app
from celery import task
import time
# Create your tests here.


# @app.task(ignore_result=True)
# @app.task
@task
def test_celery():
    print("开始")
    time.sleep(10)
    return "test celery"

