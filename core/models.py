from django.db import models
from django.shortcuts import reverse
from PIL import Image
from users.models import Vendor, Customer


class Item(models.Model):
    title = models.CharField(max_length=50)
    image = models.ImageField(default='default_item.png', upload_to='items_pics')
    price = models.PositiveIntegerField()
    description = models.TextField(max_length=250)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    units_available = models.PositiveIntegerField()
    sales = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save()
        img = Image.open(self.image.path)
        if img.height > 300 or img.width > 300:
            output_size = (300,300)
            img.thumbnail(output_size)
            img.save(self.image.path)

    def get_absolute_url(self):
        return reverse('home')


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.quantity} of {self.item.title}"


class Order(models.Model):
    order_items = models.ManyToManyField(OrderItem)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    order_datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer.user.username}"


class WishList(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)

    def __str__(self):
        return self.item.title