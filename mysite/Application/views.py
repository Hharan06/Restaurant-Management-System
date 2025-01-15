import json
from django.contrib import messages
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render,redirect
from .models import ItemFileIterator, SortedOrderProcessor, create_Account,item,order_confirm,generate_customer_id,PaymentFactory,Payment,Manager,Order_Confirm,create_account_customer
import pickle
from itertools import groupby
import operator


# Create your views here.
login_list=[]
accounts=[]
items=[]
items_2=[]
orders=[]
orders_2=[]
show_order=[]

def home(request):
    return render(request,'home.html')

def login_customer(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Load accounts from the pickle file
        with open('account_customer.pickle', 'rb') as file:
            login_list = pickle.load(file)

        # Check if the provided credentials are valid
        for account in login_list:
            if account.name == username and account.password == password:
                # Generate a customer ID (replace this logic with your preferred method)
                customer_id = generate_customer_id()

                # Store the customer ID in the session
                request.session['customer_id'] = customer_id

                # Redirect to the customer dashboard
                return render(request, 'cust_dashboard.html',{'cust_id':customer_id})

        # If credentials are invalid, show an error message
        messages.error(request, 'Invalid username or password')

    return render(request, 'customer_login.html')

def login_manager(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        with open('account.pickle', 'rb') as file:
            login_list.extend(pickle.load(file)) 

        for account in login_list:
            if account.name == username and account.password == password:
                return render(request, 'dashboard.html')

    return render(request, 'manager_login.html')

def create_account_cust(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        account = create_account_customer(username, password)
        accounts.append(account)

        with open('account_customer.pickle', 'wb') as file:
            pickle.dump(accounts, file)

        return render(request, 'customer_login.html')

    return render(request, 'create_account_customer.html')

def create_account_man(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        account = create_Account(username, password)
        accounts.append(account)

        with open('account.pickle', 'wb') as file:
            pickle.dump(accounts, file)

        return render(request, 'manager_login.html')

    return render(request, 'create_account_manager.html')

def dashboard(request):
    return render(request,'dashboard.html')

def add_food(request):
    if request.method == 'POST':
        itemname = request.POST.get('itemName')
        category = request.POST.get('category')
        price = request.POST.get('price')
        new_item = item(itemname, category, price)

        try:
            with open('food.pickle', 'rb') as file:
                items_2 = pickle.load(file)
        except (EOFError, FileNotFoundError):
            items_2 = []

        items_2.append(new_item)

        with open('food.pickle', 'wb') as file:
            pickle.dump(items_2, file)

        return render(request, 'dashboard.html')
    return render(request, 'add_food.html')

def menu(request):
    customer_id=request.session.get('customer_id')
    items_2.clear()
    try:
        with open('food.pickle', 'rb') as file:
            added_items = pickle.load(file)
        items_2.clear()
        items_2.extend(added_items)
    except EOFError:
        pass  

    with open('add_to_cart.json','r') as file:
        data=json.load(file)
        
    result=[]
    for i in data:
        if i['cust_id']==customer_id:
            result.append(i)
    print(result)
    return render(request, 'menu.html', {'dish': items_2,'cart':result})

def show_items(request):
    sorted_processor = SortedOrderProcessor()
    sorted_orders = sorted_processor.process_orders('add_to_cart.json')

    return render(request, 'show_items.html', {'sorted_orders': sorted_orders})

def add_to_cart(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cust_id = request.session.get('customer_id')
        item_name = data.get('item_name')
        item_category = data.get('item_category')
        item_price = data.get('item_price')

        confirm = order_confirm(cust_id, item_name, item_category, item_price)
        orders.append(confirm)

        with open('add_to_cart.json', 'w') as file:
            json.dump([order.__dict__ for order in orders], file)

        return redirect("menu")

def show_orders(request):
    if request.method == 'POST':
        cust_id = request.POST.get('customerId')

        # Load orders from the JSON file
        with open('add_to_cart.json', 'r') as file:
            orders = json.load(file)

        cust_order = []
        for order in orders:
            if 'cust_id' in order and order.get('cust_id') == int(cust_id):
                cust_order.append({
                    'item_name': order.get('name'),
                    'item_category': order.get('category'),
                    'item_price': order.get('price'),
                })

        return render(request, 'customer_orders.html', {'dish': cust_order})
    return render(request, 'show_orders.html')

def confirmation(request):
    if request.method == 'POST':
        payment_strategy = request.POST.get('paymentMethod')

        # Assuming Payment is a class that has a concrete implementation for the pay method
        pay = PaymentFactory(payment_strategy)
        payment = Payment(pay)
        payment_result = payment.checkout()
        # Convert the payment_result to a string representation
        result_string = str(payment_result)

        return HttpResponse(f"Payment result: {result_string}")

    return render(request, 'confirmation.html')

def delete_order(request):
    status = Manager()
    if request.method == 'POST':
        cust_id = request.POST.get('customerId')

        try:
            observer=Order_Confirm()
            status.add_customer(observer)

            status.update(cust_id,'Completed')

            with open('add_to_cart.json', 'r') as file:
                orders = json.load(file)

            # # Use a list comprehension to filter out the order with the specified customer ID
            order_delete = [order for order in orders if str(order['cust_id']) != cust_id]

            # Write the updated list of orders back to the file
            with open('add_to_cart.json', 'w') as file:
                json.dump(order_delete, file)

            # message='Completed'
            # with open('status.json', 'w') as file:
            #     json.dump({'ID':cust_id,'Status': message}, file)

            return redirect('items') 
        except Exception as e:
            return HttpResponseServerError(f"Error: {str(e)}")

    return render(request, 'delete_orders.html')

def available_item(request):
    # Load existing items from the file
    try:
        with ItemFileIterator('food.pickle') as iterator:
            for item in iterator:
                print(item)
    except (EOFError, FileNotFoundError):
        pass

    return render(request, 'available_items.html', {'dish': item})

def delete_available(request, name):
    try:
        with open('food.pickle', 'rb') as file:
            available = pickle.load(file)

        # Use a list comprehension to filter out the item with the specified name
        available = [item for item in available if item.name != name]

        # Write the updated list of items back to the file
        with open('food.pickle', 'wb') as file:
            pickle.dump(available, file)

        return redirect("available_items")
    except Exception as e:
        # Handle potential exceptions (e.g., file not found, pickle loading error)
        return HttpResponseServerError(f"Error: {str(e)}")
    
def status(request, cust_id):
    try:
        with open('status.json', 'r') as file:
            data = json.load(file)

        customer_id = data['ID']
        message = data['Status']

        if str(customer_id) == str(cust_id):
            return HttpResponse(f"Status: {message}")
        else:
            return HttpResponse("Status: In Progress")
    
    except Exception as e:
        # Handle exceptions, print the error, and return "In Progress" status
        print(f"Error: {str(e)}")
        return HttpResponse("Status: In Progress")
    
