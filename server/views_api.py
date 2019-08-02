from django.shortcuts import HttpResponse
from util.tool import login_required
from .tasks import test_celery
# Create your views here.


@login_required
def test(request):
    result = test_celery.delay()
    print(result)
    return HttpResponse('test celery!!!')

