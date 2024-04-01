from django.db import models


class Products(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=100)
    price = models.FloatField()
    file = models.FileField(upload_to='uploads')
    
    def __str__(self):
        return self.name
    
    
class OrderDetail(models.Model):
    customer_email = models.EmailField()
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    amount = models.IntegerField()
    stripe_payment_intent = models.CharField(max_length=200)
    has_paid = models.BooleanField(default=True)
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now_add=True)