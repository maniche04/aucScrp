from django.db import models

# Lot
class Lot(models.Model):
    # Source URL
    url = models.CharField(max_length=2500)
    # Source Website
    source = models.CharField(max_length=100)
    auction_title = models.CharField(max_length=500)
    lot_number = models.CharField(max_length=200)
    name = models.CharField(max_length=500)
    description = models.CharField(max_length=5000, null=True)
    image_url = models.CharField(max_length=5000, null=True)
    details_url = models.CharField(max_length=5000, null=True)
    # Sale and Pricing
    is_sold = models.BooleanField()
    sold_price = models.DecimalField(max_digits=30, decimal_places=2, null=True)
    sold_currency = models.CharField(max_length=50, null=True)
    # Attributes
    grading = models.CharField(max_length=100, null=True)
    brand = models.CharField(max_length=500, null=True)
    model = models.CharField(max_length=500, null=True)
    year = models.CharField(max_length=500, null=True)
    reference = models.CharField(max_length=500, null=True)
    case_no = models.CharField(max_length=500, null=True)
    numbers = models.CharField(max_length=500, null=True)
    caliber = models.CharField(max_length=500, null=True)
    bracelet = models.CharField(max_length=500, null=True)
    signature = models.CharField(max_length=500, null=True)
    accessories = models.CharField(max_length=500, null=True)
    dimensions = models.CharField(max_length=500, null=True)

# Lot Pricing
class LotPrice(models.Model):
    lot = models.ForeignKey(Lot, on_delete=models.CASCADE)
    currency = models.CharField(max_length=100)
    min_price = models.DecimalField(max_digits=30, decimal_places=2)
    max_price = models.DecimalField(max_digits=30, decimal_places=2)


