from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from .models import *
from django.http import JsonResponse
import json
import datetime
from .utils import cookieCart, cartData,guestOrder

# Create your views here.


def store(request):
    data = cartData(request)

    cartItems = data['cartItems']
    products = Product.objects.all()
    context = {'products': products, 'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/store.html', context)


def cart(request):
    data = cookieData(request)

    items = data['items']
    order = data['order']
    cartItems = data['cartItem']

    context = {'items': items, 'order': order,
               'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/cart.html', context)


def checkout(request):
    data = cookieData(request)
    cartItems = data['cartItems']
    order = data['order']
    ittems = data['items']

    context = {'items': items, 'order': order,
               'cartItems': cartItems, 'shipping': False}
    return render(request, 'store/checkout.html', context)


def updateItem(request):
    data = json.loads(request.data)
    productId = data['productId']
    action = data['action']
    print('Action;', action)
    print('Product:', productId)

    customer = request.user.customer
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(
        customer=customer, complete=False)

    orderItem, create = OrderItem.objects.get_or_create(
        order=order, product=product)
    if action == "add":
        orderItem.quantity = (orderItem.quantity+1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity+1)
    orderItem.save()
    if orderItem.quantity <= 0:
        orderItem.delete()
    return JsonResponse("Item was added ", safe=False)


@csrf_exempt
def processOrder(request):
    transaction_id = datetime.datetime.now().timestamp()
    data = json.loads(request.data)
    if request.user.is_authenticated:
        customer = request.user.customer
        order, created = Order.objects.get_or_create(
            customer=customer, complete=False)

    else:

        customer,order=guestOrder(request,data)
    total = float(data['form']['total'])
    order.transaction_id = transaction_id

    if total == order.get_cart_total:
        order.complete = True
    order.save()
    if order.shipping == True:
        ShippingAddress.objects.create(
            customer=customer,
            order=order,
            address=data['shippingInfo']['address'],
            city=data['shippingInfo']['city'],
            zipcode=data['shippingInfo']['zipcode'],
        )
    return JsonResponse("Checkout is being processed", safe=False)
