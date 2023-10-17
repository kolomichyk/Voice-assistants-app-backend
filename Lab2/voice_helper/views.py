from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
from voice_helper.models import Actions
from  django.db import connection
from django.shortcuts import redirect

def ActionsList(request):
    pattern = request.GET.get('name_of_item', '')
    return render(request, 'orders.html', {'data' : {
        'current_date': date.today(),
        'actions': Actions.objects.all().filter(status=0, title__icontains=pattern),
        'input_value': pattern
    }})

def GetAction(request, id):
    print(Actions.objects.filter(id=id)[0].title)
    return render(request, 'order.html', {'data' : {
        'current_date': date.today(),
        'Actions': Actions.objects.filter(id=id)[0]
    }})

def DeleteRecord(request, id):
    with connection.cursor() as cursor:
        req = "UPDATE voice_helper_Actions SET status = 1 WHERE id = %s"
        cursor.execute(req, [id])
    return redirect('http://localhost:8000/')