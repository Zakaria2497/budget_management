from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db.models import Sum

## Required this one for me

class Account(models.Model):
    name = models.CharField(max_length=45) 
    alloted = models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Total Allotment",null=True, blank=True)
    actual_recieved = models.DecimalField(decimal_places=2, max_digits=12,verbose_name="Received from govt", null=True, blank=True,default=0.0)
    acc_balance = models.DecimalField(decimal_places=2, max_digits=12,verbose_name="Total After Adjustment",null=True, blank=True, default=0.0)
    adjusted = models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Fund with Adjustment",default=0.0)
    amount = models.DecimalField(decimal_places=2, max_digits=12,verbose_name="Last Transfer",null=True, blank=True, default=0.0)
    total_after_adjustment = models.DecimalField(decimal_places=2,max_digits=15, verbose_name="Total after adjustment for showing", null=True, blank=True, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.name  


class History(models.Model):
    account = models.ForeignKey(Account,on_delete=models.CASCADE, null=True, blank=True)
    update_name = models.CharField(max_length=75, null=True, blank=True)
    alloted = models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Total Allotment",null=True, blank=True)
    actual_recieved = models.DecimalField(decimal_places=2, max_digits=12,verbose_name="Received from govt", null=True, blank=True,default=0.0)
    acc_balance = models.DecimalField(decimal_places=2, max_digits=12,verbose_name="Total After Adjustment",null=True, blank=True, default=0.0)
    adjusted = models.DecimalField(decimal_places=2, max_digits=12, verbose_name="Fund with Adjustment",default=0.0)
    amount = models.DecimalField(decimal_places=2, max_digits=12,verbose_name="Last Transfer",null=True, blank=True, default=0.0)
    total_after_adjustment = models.DecimalField(decimal_places=2,max_digits=15, verbose_name="Total after adjustment for showing", null=True, blank=True, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
 
    def __str__(self):
        return self.account.name  



## Required This One for me
class Transfer(models.Model):
    name = models.ForeignKey(Account,on_delete=models.CASCADE,null=True, blank=True)
    vendor = models.CharField(max_length=45) #ex. Taco Bell, Nordstrom, Chase Bank, etc
    description = models.CharField(max_length=45) #ex. Pay Chase Card off with BoA Checking, Buy Gas at Arco with Debit Card, etc
    amount = models.DecimalField(decimal_places=2, max_digits=12)
    debit_acc = models.ForeignKey(Account, related_name="transfers_debit", on_delete=models.CASCADE)
    credit_acc = models.ForeignKey(Account, related_name="transfers_credit", on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def clean(self):

        #### For Credit 
        total = self._meta.model.objects.filter(credit_acc=self.credit_acc).aggregate(Sum('amount'))

        if not self._state.adding:
            total = self._meta.model.objects.filter(credit_acc=self.credit_acc).exclude(pk=self.id).aggregate(Sum('amount'))
            print("Zakakkakkakkak")
        if total['amount__sum'] is None:
            total['amount__sum'] = 0
        
        if self.amount + total['amount__sum'] > self.credit_acc.alloted:    
            raise ValidationError(f'{self.amount}  Money Receive====== n addition with previous total {total["amount__sum"]} exceeds budget of RDPP {self.credit_acc} (DBT {self.credit_acc.alloted})')
       
        
        ### For Debit

        total = self._meta.model.objects.filter(debit_acc=self.debit_acc).aggregate(Sum('amount'))

        if not self._state.adding:
            total = self._meta.model.objects.filter(debit_acc=self.debit_acc).exclude(pk=self.id).aggregate(Sum('amount'))
        if total['amount__sum'] is None:
            total['amount__sum'] = 0
       
       
        if self.amount + total['amount__sum'] > self.debit_acc.alloted:    
            raise ValidationError(f'{self.amount} Money Giving======= in addition with previous total {total["amount__sum"]} exceeds budget of RDPP {self.debit_acc} (DBT {self.debit_acc.alloted})')

        if self.amount + total['amount__sum'] > self.debit_acc.acc_balance:    
            raise ValidationError(f'{self.amount} in addition with previous total {total["amount__sum"]} exceeds budget of RDPP {self.debit_acc} (DBT {self.debit_acc.acc_balance})')


    def __str__(self):
        return self.credit_acc.name









