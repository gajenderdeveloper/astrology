from django.db import models

# Create your models here.


class Sector(models.Model):
    name = models.CharField(max_length=50,unique=True)   
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        """
        :return: the Category name
        """
        return self.name
    

class SectorSymbol(models.Model):
    sector = models.ForeignKey(Sector, on_delete=models.CASCADE, related_name='sector_details', verbose_name='Sectoor ID')
    symbol = models.CharField(max_length=50)   
    company_name = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        """
        :return: the symbol name
        """
        return self.symbol
    