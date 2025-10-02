from django.db import models
from django.utils import timezone
from django.urls import reverse

# Create your models here.

class Transaction(models.Model):
    """Model for recording expenses"""
    
    CATEGORY_CHOICES = [
        ('Food', 'Food'),
        ('Fuel', 'Fuel'),
        ('Bills', 'Bills'),
        ('Shopping', 'Shopping'),
        ('Other', 'Other'),
    ]
    
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Expense amount")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='Other')
    date = models.DateField(default=timezone.now)
    note = models.TextField(blank=True, null=True, help_text="Optional note about the expense")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = 'Transaction'
        verbose_name_plural = 'Transactions'
    
    def __str__(self):
        return f"{self.category} - ${self.amount} on {self.date}"
    
    def get_absolute_url(self):
        return reverse('transaction_detail', kwargs={'pk': self.pk})
