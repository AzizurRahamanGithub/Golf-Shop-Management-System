from django.db import models
from django.db import models
from apps.auths.models import CustomUser
from apps.products.models import Shop, Package
from apps.cart.models import Cart


class Booking(models.Model):
    
    STATUS_CHOICES=[
            ('progress', 'Progress'),
            ('complete', 'Complete')
        ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="bookings")
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    booking_status= models.CharField(max_length=12, choices=STATUS_CHOICES, default='progress')
    number_of_guests = models.PositiveIntegerField()
    shop_type = models.CharField(max_length=100)

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

    street_address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=20)

    package = models.ForeignKey(Package, on_delete=models.SET_NULL, null=True, blank=True)
    shop = models.ForeignKey(Shop, on_delete=models.SET_NULL, null=True, blank=True)
    
    shops = models.JSONField(default=list, blank=True)
    packages = models.JSONField(default=list, blank=True)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    damage_waiver = models.BooleanField(default=False)
    
    signature= models.CharField(max_length=300, blank=True, null=True)
    print_name= models.CharField(max_length=300, blank=True, null=True)
    date= models.DateField(blank=True ,null=True)
    signature_image= models.CharField(max_length=300, blank=True, null=True)
    
    payment_id= models.CharField(max_length= 300 , blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.full_name} ({self.start_date})"

