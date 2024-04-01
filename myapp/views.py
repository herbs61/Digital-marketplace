from django.shortcuts import render,get_object_or_404,reverse
from .models import Products,OrderDetail
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django .http import JsonResponse,HttpResponseNotFound
import stripe,json


def index(request):
    product = Products.objects.all()
    context = {
        'product': product}
    return render(request, 'myapp/index.html', context)


def detail(request, id):
    products = get_object_or_404(Products, id=id)
    stripe_pusblishable_key = settings.STRIPE_PUBLISHABLE_KEY
    context = {'products': products,
               'stripe_publishable_key': stripe_pusblishable_key
               }
    return render(request, 'myapp/detail.html', context)


@csrf_exempt
def create_checkout_session(request, id):
    request_data = json.load(request.body)
    products = Products.objects.get(id=id)
    stripe.api_key = settings.STRIPE_SECRET_KEY
    checkout_session = stripe.checkout.Session.create(
        customer_eamil = request_data['email'],
        payment_method_types = ['card'],
        line_items = [
            {
                'price_data':{
                    'currency':'usd',
                    'product_data':{
                        'name':products.name,       
                    },
                    'unit_amount':int(products.price * 100)
                },
                'quantity':1,
            }
        ],
        mode='payment',
        success_url = request.build_absolute_url(reverse('success')) +
        "?session_id={CHECKOUT_SESSION_ID}",
        cancel_url = request.build_absolute_url(reverse('failed')),
    )
    
    order = OrderDetail()
    order.customer_email = request_data['email']
    order.products = products
    order.stripe_payment_intent = checkout_session['payment_intent']
    order.amount = int(products.price)
    order.save()
    
    return JsonResponse({'sessionId': checkout_session.id})


def payment_success_view(request):
    session_id = request.GET.get('session_id')
    if session_id is None:
        return HttpResponseNotFound()
    stripe.api_key = settings.STRIP_SECRET_KEY
    session = stripe.checkout.Session.retrieve(session_id)
    order = get_object_or_404(OrderDetail, stripe_payment_intent= session.payment_intent)
    order.has_paid= True
    order.save()
    context = {
        'order': order
    }
    
    return render(request, 'myapp/payment_success.htm', context)


def payment_failed_view(request):
    return render(request, 'myapp/failed.html')