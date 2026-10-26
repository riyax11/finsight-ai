from django.db import models

class Client(models.Model):
    """Represents a bank customer."""
    client_id = models.AutoField(primary_key=True)
    gender = models.CharField(max_length=10, choices=[('M', 'Male'), ('F', 'Female')], null=True, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    
    def __str__(self):
        return f"Client {self.client_id}"

class Account(models.Model):
    """Represents a bank account owned by a client."""
    account_id = models.AutoField(primary_key=True)
    date_created = models.DateField(null=True, blank=True)
    frequency = models.CharField(max_length=50) 
    
    def __str__(self):
        return f"Account {self.account_id}"

class Disposition(models.Model):
    """Links Clients to Accounts (Owner vs Disponent)."""
    disp_id = models.AutoField(primary_key=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(max_length=50) 
    
    def __str__(self):
        return f"{self.type}: {self.client} -> {self.account}"

class Loan(models.Model):
    """Loan records linked to an account."""
    loan_id = models.AutoField(primary_key=True)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    date_granted = models.DateField(null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    duration = models.IntegerField()
    payments = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50) # Expanded length for full text

    def __str__(self):
        return f"Loan {self.loan_id} ({self.status})"

class Transaction(models.Model):
    """The main ledger."""
    trans_id = models.AutoField(primary_key=True)
    account_id = models.IntegerField() # Using integer to avoid FK constraint issues during bulk load
    date = models.DateField()
    type = models.CharField(max_length=50) 
    operation = models.CharField(max_length=50, null=True, blank=True) 
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    balance = models.DecimalField(max_digits=12, decimal_places=2)
    k_symbol = models.CharField(max_length=50, null=True, blank=True)
    bank = models.CharField(max_length=50, null=True, blank=True) 
    account_partner = models.CharField(max_length=50, null=True, blank=True) 

    class Meta:
        indexes = [
            models.Index(fields=['date']),
            models.Index(fields=['type']),
        ]

    def __str__(self):
        return f"Txn {self.trans_id}: {self.amount}"