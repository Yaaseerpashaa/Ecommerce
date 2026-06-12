from django.shortcuts import render,redirect
from ecommerceapp.models import Contact,Product,OrderUpdate,Orders
from django.contrib import messages
from math import ceil
from django.conf import settings
import json
from django.views.decorators.csrf import  csrf_exempt
import random
from django.shortcuts import render
from .models import Orders, OrderUpdate

# Create your views here.



def index(request):
    allProds = []
    catprods = Product.objects.values('category', 'id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])
    params= {'allProds': allProds}
    return render(request, "index.html", params)

    
def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"we will get back to you soon..")
        return render(request,"contact.html")


    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")


def checkout(request):
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')

    if request.method == "POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        # Save the order first
        order = Orders(
            items_json=items_json,
            name=name,
            amount=amount,
            email=email,
            address1=address1,
            address2=address2,
            city=city,
            state=state,
            zip_code=zip_code,
            phone=phone
        )
        order.save()

        # Simulate payment status
        status = random.choice(['PAID', 'FAILED'])  # Randomly decide payment status
        oid = str(order.order_id) + "ShopyCart"

        order.oid = oid
        order.amountpaid = amount if status == "PAID" else "0"
        order.paymentstatus = status
        order.save()

        # Save order update
        update_msg = "The order has been placed successfully." if status == "PAID" else "The order was not placed. Payment failed."
        update = OrderUpdate(order_id=order.order_id, update_desc=update_msg)
        update.save()

        # Redirect to success or failure page
        if status == "PAID":
            messages.success(request, f"Thanks for your order! Order ID: {oid}")
            return render(request, 'success.html', {'order': order})
        else:
            messages.error(request, f"Payment Failed for Order ID: {oid}")
            return render(request, 'failed.html', {'order': order})

    return render(request, 'checkout.html')


def profile(request):
    if not request.user.is_authenticated:
        return redirect("login")  # Optional: if you use authentication

    currentuser_email = request.user.email
    orders = Orders.objects.filter(email=currentuser_email)
    
    order_status = []
    for order in orders:
        updates = OrderUpdate.objects.filter(order_id=order.order_id).order_by('-timestamp')
        order_status.append({
            'order': order,
            'updates': updates,
        })

    return render(request, 'profile.html', {'order_status': order_status})


