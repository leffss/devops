from django.shortcuts import render, HttpResponse
from util.tool import login_required
from django.http import JsonResponse
from .tasks import task_test
# Create your views here.


@login_required
def test_api(request):
    task_test.delay()
    return JsonResponse({"code": 200, "err": 'test ansible api'})

