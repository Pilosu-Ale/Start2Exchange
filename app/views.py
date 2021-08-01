from django.shortcuts import render, HttpResponseRedirect
from .models import Profile, Order
from .forms import OrderForm
from django.utils import timezone


def homepage(request):
    orderList = Order.objects.filter().order_by('price')
    sellOrderList = Order.objects.filter(position="SELL", status="OPEN").order_by('price')
    buyOrderList = Order.objects.filter(position="BUY", status="OPEN").order_by('-price')

    if buyOrderList and sellOrderList:
        buyOrder = buyOrderList[0]
        sellOrder = sellOrderList[0]
        while buyOrderList and sellOrderList and buyOrder.price >= sellOrder.price:
            buyOrderProfile = Profile.objects.get(user=buyOrder.profile.user)
            sellOrderProfile = Profile.objects.get(user=sellOrder.profile.user)
            if buyOrder.quantity < sellOrder.quantity:
                buyOrder.status = "CLOSED"  # chiudo l'ordine BUY
                buyOrder.save()
                sellOrder.quantity -= buyOrder.quantity  # sottraggo i BTC dell'ordine BUY al vecchio SELL che resta aperto
                sellOrder.save()

                buyOrderProfile.balance -= sellOrder.price * buyOrder.quantity  # aggiorno il profilo dell'ordine BUY
                buyOrderProfile.BTC_wallet += buyOrder.quantity
                buyOrderProfile.save()

                sellOrderProfile.balance += sellOrder.price * buyOrder.quantity  # aggiorno il profilo dell'ordine SELL
                sellOrderProfile.BTC_wallet -= buyOrder.quantity
                sellOrderProfile.save()

            elif buyOrder.quantity == sellOrder.quantity:
                sellOrder.status = "CLOSED"  # chiudo l'ordine SELL
                sellOrder.save()
                buyOrder.status = "CLOSED"  # chiudo l'ordine BUY
                buyOrder.save()

                buyOrderProfile.balance -= sellOrder.price * buyOrder.quantity  # aggiorno il profilo dell'ordine buy
                buyOrderProfile.BTC_wallet += buyOrder.quantity
                buyOrderProfile.save()

                sellOrderProfile.balance += sellOrder.price * buyOrder.quantity  # aggiorno il profilo dell'ordine SELL
                sellOrderProfile.BTC_wallet -= buyOrder.quantity
                sellOrderProfile.save()

            else:
                buyOrder.quantity -= sellOrder.quantity  # sottraggo i BTC dell'ordine SELL all'ordine BUY che resta aperto
                buyOrder.save()
                sellOrder.status = "CLOSED"  # chiudo l'ordine SELL
                sellOrder.save()

                buyOrderProfile.balance -= sellOrder.price * sellOrder.quantity  # aggiorno il profilo dell'ordine BUY
                buyOrderProfile.BTC_wallet += sellOrder.quantity
                buyOrderProfile.save()

                sellOrderProfile.balance += sellOrder.price * sellOrder.quantity  # aggiorno il profilo dell'ordine SELL
                sellOrderProfile.BTC_wallet -= sellOrder.quantity
                sellOrderProfile.save()

            sellOrderList = Order.objects.filter(position="SELL", status="OPEN").order_by('price')
            buyOrderList = Order.objects.filter(position="BUY", status="OPEN").order_by('-price')

    if request.method == "POST":
        form = OrderForm(request.POST, user=request.user)
        if form.is_valid():
            order = form.save(commit=False)
            order.position = form.cleaned_data['position']
            order.price = form.cleaned_data['price']
            order.quantity = form.cleaned_data['quantity']
            order.status = "OPEN"
            order.datetime = timezone.now()
            order.profile = Profile.objects.get(user=request.user)

            order.save()

            return HttpResponseRedirect("/")

    else:
        form = OrderForm()

    return render(
        request, "app/homepage.html", {
            'orderList': orderList,
            'form': form,
            'sellOrderList': sellOrderList,
            'buyOrderList': buyOrderList
        }
    )


def profitPage(request):
    profileList = Profile.objects.all()

    return render(request, "app/profit.html", {'profileList': profileList})


def myProfile(request):
    profile = Profile.objects.get(user=request.user)
    myOrderList = Order.objects.filter(profile=profile)
    return render(request, "app/my_profile.html", {'profile': profile, 'myOrderList': myOrderList})
