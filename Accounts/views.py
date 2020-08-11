from django.shortcuts import render,redirect
from django.http import  HttpResponse
from django.forms import inlineformset_factory
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import Group
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import  login_required
from .decorators import unauthenticated_user, allowed_user, admin_only
from .models import *
from .forms import *
from .filters import  *





# Create your views here.
@unauthenticated_user
def register_page(request):
	form = CreateUserForm()
	if request.method == 'POST':
		form = CreateUserForm(request.POST)
		if form.is_valid():
			user = form.save()

			messages.success(request, 'Account Created Successfully')
			return redirect('login_page')


	tempvar= {'form': form}
	return render(request, 'Accounts/register.html', tempvar)



@unauthenticated_user
def login_page(request):
	if request.method == 'POST':
		username = request.POST.get('username')
		password = request.POST.get('password')

		user = authenticate(request, username=username, password=password)


		if user is not None :
			login(request,user)
			return redirect('home')
		else:
			messages.info(request, 'Username or Password Incorrect')



	tempvar= {}
	return render(request, 'Accounts/login.html', tempvar)



@login_required(login_url='login_page')
def logout_user(request):
	logout(request)
	return redirect('login_page')



@login_required(login_url='login_page')
@admin_only
def home(request):
	customers = Customer.objects.all()
	orders = Order.objects.all()

	total_customers = customers.count()
	total_orders = orders.count()
	delivered = orders.filter(status="Delivered").count()
	pending = orders.filter(status="Pending").count()


	template_var = {'customers':customers,'orders':orders,
					'delivered':delivered, 'pending':pending,
					'total_orders':total_orders, 'total_customers':total_customers}

	return render(request, 'Accounts/dashboard.html', template_var)


@login_required(login_url='login_page')
@allowed_user(allowed_roles=['customer'])
def user_page(request):
	orders = request.user.customer.order_set.all()
	total_orders = orders.count()
	delivered = orders.filter(status="Delivered").count()
	pending = orders.filter(status="Pending").count()


	tempvar ={'orders':orders, 'delivered':delivered, 'pending':pending, 'total_orders':total_orders}
	return render(request, 'Accounts/user.html', tempvar)



@login_required(login_url='login_page')
@allowed_user(allowed_roles=['admin'])
def products(request):
	products = Product.objects.all()
	return render(request, 'Accounts/products.html', {'products':products})



@login_required(login_url='login_page')
@allowed_user(allowed_roles=['admin'])
def customer(request,key):
	customer = Customer.objects.get(id=key)
	orders = customer.order_set.all()
	orders_count = orders.count()
	MyFilter = OrderFilter(request.GET, queryset=orders)
	orders = MyFilter.qs
	tempvar = {'customer':customer, 'orders':orders,
			   'orders_count':orders_count, 'MyFilter':MyFilter}
	return render(request, 'Accounts/customer.html', tempvar)



@login_required(login_url='login_page')
@allowed_user(allowed_roles=['customer'])
def account_settings(request):
	customer = request.user.customer
	form = CustomerForm(instance=customer)
	if request.method == 'POST':
		form = CustomerForm(request.POST,request.FILES, instance=customer)
		if form.is_valid():
			form.save()

	tempvar = {'form': form}
	return render(request, 'Accounts/account_settings.html', tempvar)




@login_required(login_url='login_page')
@allowed_user(allowed_roles=['admin'])
def create_order(request, pk):
	OrderFormSet = inlineformset_factory(Customer, Order, fields=('product', 'status'), extra=5)
	customer = Customer.objects.get(id=pk)
	formset = OrderFormSet(queryset=Order.objects.none(), instance=customer)
	#form = OrderForm(initial={'customer':customer})
	if request.method == 'POST':
		formset = OrderFormSet(request.POST,instance=customer)
		if formset.is_valid():
			formset.save()
			return redirect('/')

	tempvar ={'formset':formset}		
	return render(request, 'Accounts/order_form.html', tempvar)



@login_required(login_url='login_page')
def update_order(request, pk):
	order = Order.objects.get(id=pk)
	form = OrderForm(instance=order)
	if request.method == 'POST':
		form = OrderForm(request.POST, instance=order)
		if form.is_valid():
			form.save()
		return redirect('/')

	tempvar = {'form':form, 'order':order}
	return render(request, 'Accounts/order_form.html', tempvar)



@login_required(login_url='login_page')
def delete_order(request, pk):
	order = Order.objects.get(id=pk)
	if request.method == 'POST':
		order.delete()
		return redirect('/')

	tempvar = {'item':order}
	return render(request, 'Accounts/delete.html', tempvar)



