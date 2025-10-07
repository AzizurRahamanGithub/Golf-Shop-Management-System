from django.db import models
from apps.auths.models import CustomUser
from apps.products.models import Shop, Package

class Cart(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(item.total_price() for item in self.items.all())

    def __str__(self):
        return f"Cart ({self.user})"


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    shop = models.ForeignKey(Shop, on_delete=models.CASCADE, null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        total = 0
        # Add shop price if exists
        if self.shop:
            total += self.shop.price * self.quantity
        # Add package price if exists
        if self.package:
            total += self.package.price * self.quantity
        return total

    def __str__(self):
        items = []
        if self.shop:
            items.append(self.shop.name)
        if self.package:
            items.append(self.package.name)
        item_names = " + ".join(items)
        return f"{item_names} × {self.quantity}"