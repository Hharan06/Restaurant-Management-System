import pickle
from django.db import models
import json
from itertools import groupby
from abc import ABC,abstractmethod

# Create your models here.
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            instance = super().__call__(*args, **kwargs)
            cls._instances[cls] = instance
        return cls._instances[cls]

class Create_Account(metaclass=SingletonMeta):
    def __init__(self, name, password):
        self.name = name
        self.password = password

def create_Account(name, password):
    return Create_Account(name, password)

class Create_Account_customer:
    def __init__(self, name, password):
        self.name = name
        self.password = password

def create_account_customer(name,password):
    return Create_Account_customer(name,password)

class Item:
    def __init__(self, name, category, price):
        self.name = name
        self.category = category
        self.price = price

    def get_content(self):
        return {
            'Name': self.name,
            'Category': self.category,
            'Price': self.price
        }

def item(name,category,price):
    return Item(name, category, price)

class Observer(ABC):
    @abstractmethod
    def update(self):
        pass

class Orders:
    def __init__(self,cust_id,name,category,price):
        self.cust_id=cust_id
        self.name=name
        self.category=category
        self.price=price

class Order_Confirm(Observer):
    def update(self,cust_id,message):
        with open('status.json','w') as file:
            json.dump({'ID':cust_id,'Status':message},file)

class Manager(Order_Confirm):
    def __init__(self):
        self.customers=[]

    def add_customer(self,customer):
        self.customers.append(customer)

    def update(self, cust_id, message):
        for i in self.customers:
            i.update(cust_id,message)

def order_confirm(cust_id,name,category,price):
    return Orders(cust_id,name, category, price)

def generate_customer_id():
    import random
    return random.randint(1000, 9999)

class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self):
        pass

class Card(PaymentStrategy):
    def pay(self):
        return "Payment is done through Card"
    
class Cash(PaymentStrategy):
    def pay(self):
        return "Payment is done through Cash"
    
class UPI(PaymentStrategy):
    def pay(self):
        return "Payment is done through UPI"
    
class Payment:
    def __init__(self,paymentstrategy):
        self.payment=paymentstrategy

    def checkout(self):
       return self.payment.pay()

def PaymentFactory(payment):
    if payment=='Card':
        return Card()
    if payment=='Cash':
        return Cash()
    if payment=='UPI':
        return UPI()

class ItemFileIterator:
    def __init__(self, filename):
        self.filename = filename
        self.file = None

    def __enter__(self):
        self.file = open(self.filename, 'rb')
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.file:
            self.file.close()

    def __iter__(self):
        return self

    def __next__(self):
        try:
            item = pickle.load(self.file)
            result=[]
            for i in range(len(item)):
                data=Item.get_content(item[i])
                result.append(data)
            return result
        except EOFError:
            raise StopIteration
        
class OrderProcessor:
    def load_orders(self, filename):
        orders = []
        with open(filename, 'r') as file:
            confirm = json.load(file)
        orders.extend(confirm)
        return orders

class SortedOrderProcessor(OrderProcessor):
    def process_orders(self, filename):
        orders = self.load_orders(filename)
        sorted_orders = sorted(orders, key=lambda x: x['cust_id'])
        return sorted_orders