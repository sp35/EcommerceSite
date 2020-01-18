from django.contrib import admin
from core.models import *

admin.site.register([ Item, OrderItem, Order, WishList ])