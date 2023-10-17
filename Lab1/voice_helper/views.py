from django.shortcuts import render
from django.http import HttpResponse
from datetime import date
import re
import logging

def hello(request):
    return render(request, 'index.html', {
        'current_date': date.today()
    })

def GetOrders(request):
    pattern = request.GET.get('name_of_item')
    data = GetData(0)
    
    if pattern:
        data['collection']['input_value'] = pattern
        result_of_search = []
        for i in data['collection']['orders']:
            if re.search(pattern, i['title']):
                result_of_search.append(i)

        data['collection']['orders'] = result_of_search

    return render(request, 'orders.html', data)

def GetOrder(request, id):
    data = GetData(id)
    return render(request, 'order.html', {'data': data
    })

def GetData(id):
    data = {'collection' : {
        'current_date': date.today(),
        'orders': [
            {'title': 'Разработка голосового помощника', 'id': 1, 'price': "Договорная", "img": "img/1.jpg", "description" : "Разработаем новое решение для вашего бизнеса!\nВ данную услугу входит сбор, анализ данных, создание голосового помощника. Для уточнения деталей услуги свяжитесь с нами."},
            {'title': 'Настройка голосового помощника', 'id': 2, 'price': "15000 руб.", "img": "img/2.jpg", "description": "Настроим вашего голосового помощника под ваши нужды! Для уточнения деталей услуги свяжитесь с нами."},
            {'title': 'Оптимизация голосового помощника', 'id': 3, 'price': "30000 руб.", "img": "img/3.jpg", "description": "Опитимизируем вашего голосового помощника! Для уточнения деталей услуги свяжитесь с нами."},
            {'title': 'Консультация', 'id': 4, 'price': "Бесплатно", "img": "img/4.jpg", "description": "Проконсультируем по всем вопросам по созданию голосовых помошников, расскажем о нас и нашей крутой команде! Найдём совместное решение для вашего бизнеса!"},
        ],
    'input_value' : ''
    }}
    if id == 0:
        return data
    else:
        for i in data['collection']['orders']:
            if i['id'] == id:
                return i
    return -1
    
# Create your views here.
