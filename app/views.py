from django.shortcuts import render, HttpResponseRedirect
from .models import Profile, Order
from .forms import OrderForm
from django.utils import timezone


def homepage(request):
    orderList = Order.objects.filter().order_by('price')
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

            if order.position == "BUY" and sellOrderList:
                sellOrder = sellOrderList[0]
                if order.price >= sellOrder.price:
                    newOrderProfile = Profile.objects.get(user=order.profile.user)
                    sellOrderProfile = Profile.objects.get(user=sellOrder.profile.user)
                    if order.quantity < sellOrder.quantity:
                        order.status = "CLOSED"  # chiudo il nuovo ordine BUY
                        order.save()
                        sellOrder.quantity -= order.quantity  # sottraggo i BTC del nuovo ordine al vecchio SELL che resta aperto
                        sellOrder.save()

                        newOrderProfile.balance -= sellOrder.price * order.quantity  # aggiorno il profilo del nuovo ordine
                        newOrderProfile.BTC_wallet += order.quantity
                        newOrderProfile.save()

                        sellOrderProfile.balance += sellOrder.price * order.quantity  # aggiorno il profilo del vecchio ordine SEL
                        sellOrderProfile.BTC_wallet -= order.quantity
                        sellOrderProfile.save()

                    elif order.quantity == sellOrder.quantity:
                        sellOrder.status = "CLOSED"  # chiudo il vecchio ordine SELL
                        sellOrder.save()
                        order.status = "CLOSED"  # chiudo il nuovo ordine BUY
                        order.save()

                        newOrderProfile.balance -= sellOrder.price * order.quantity  # aggiorno il profilo del nuovo ordine
                        newOrderProfile.BTC_wallet += order.quantity
                        newOrderProfile.save()

                        sellOrderProfile.balance += sellOrder.price * order.quantity  # aggiorno il profilo del vecchio ordine SEL
                        sellOrderProfile.BTC_wallet -= order.quantity
                        sellOrderProfile.save()

                    else:
                        order.quantity -= sellOrder.quantity  # sottraggo i BTC del vecchio ordine SELL al nuovo che resta aperto
                        order.save()
                        sellOrder.status = "CLOSED"  # chiudo il vecchio ordine SELL
                        sellOrder.save()

                        newOrderProfile.balance -= sellOrder.price * sellOrder.quantity  # aggiorno il profilo del nuovo ordine
                        newOrderProfile.BTC_wallet += sellOrder.quantity
                        newOrderProfile.save()

                        sellOrderProfile.balance += sellOrder.price * sellOrder.quantity  # aggiorno il profilo del vecchio ordine SEL
                        sellOrderProfile.BTC_wallet -= sellOrder.quantity
                        sellOrderProfile.save()

                else:
                    order.save()

            elif order.position == "SELL" and buyOrderList:
                buyOrder = buyOrderList[0]
                if order.price <= buyOrder.price:
                    newOrderProfile = Profile.objects.get(user=order.profile.user)
                    buyOrderProfile = Profile.objects.get(user=buyOrder.profile.user)
                    if order.quantity < buyOrder.quantity:
                        order.status = "CLOSED"  # chiudo il nuovo ordine SELL
                        order.save()
                        buyOrder.quantity -= order.quantity  # sottraggo i BTC del nuovo ordine al vecchio BUY che resta aperto
                        buyOrder.save()

                        newOrderProfile.balance += buyOrder.price * order.quantity  # aggiorno il profilo del nuovo ordine
                        newOrderProfile.BTC_wallet -= order.quantity
                        newOrderProfile.save()

                        buyOrderProfile.balance -= buyOrder.price * order.quantity  # aggiorno il profilo del vecchio ordine SEL
                        buyOrderProfile.BTC_wallet += order.quantity
                        buyOrderProfile.save()

                    elif order.quantity == buyOrder.quantity:
                        order.status = "CLOSED"  # chiudo il nuovo ordine SELL
                        order.save()
                        buyOrder.status = "CLOSED"  # chiudo il vecchio ordine BUY
                        buyOrder.save()

                        newOrderProfile.balance += buyOrder.price * order.quantity  # aggiorno il profilo del nuovo ordine
                        newOrderProfile.BTC_wallet -= order.quantity
                        newOrderProfile.save()

                        buyOrderProfile.balance -= buyOrder.price * order.quantity  # aggiorno il profilo del vecchio ordine SEL
                        buyOrderProfile.BTC_wallet += order.quantity
                        buyOrderProfile.save()

                    else:
                        buyOrder.status = "CLOSED"  # chiudo il vecchio ordine BUY
                        buyOrder.save()

                        order.quantity -= buyOrder.quantity  # sottraggo i BTC del vecchio ordine BUY al nuovo che resta aperto
                        order.save()

                        newOrderProfile.balance += buyOrder.price * buyOrder.quantity  # aggiorno il profilo del nuovo ordine
                        newOrderProfile.BTC_wallet -= buyOrder.quantity
                        newOrderProfile.save()

                        buyOrderProfile.balance -= buyOrder.price * buyOrder.quantity  # aggiorno il profilo del vecchio ordine SEL
                        buyOrderProfile.BTC_wallet += buyOrder.quantity
                        buyOrderProfile.save()

                else:
                    order.save()
            else:
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
