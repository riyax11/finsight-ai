import csv
import pandas as pd
from datetime import datetime
from django.core.management.base import BaseCommand
from core.models import Client, Account, Disposition, Loan, Transaction
# Note: We are skipping Card/Order models for the MVP to keep it simple, 
# but you can add them easily if needed later.

class Command(BaseCommand):
    help = 'Loads cleaned banking data from /data/processed into PostgreSQL'

    def handle(self, *args, **kwargs):
        base_path = '../data/processed' # Adjust if your path is different
        
        print(" STARTING DATABASE INGESTION ")

        # 1. CLIENTS
        print("Loading Clients.")
        clients = []
        df_client = pd.read_csv(f'{base_path}/clean_client.csv')
        for _, row in df_client.iterrows():
            clients.append(Client(
                client_id=row['client_id'],
                gender=row['gender'],
                birth_date=row['birth_date']
            ))
        Client.objects.all().delete() # Clear old data
        Client.objects.bulk_create(clients)
        print(f"Inserted {len(clients)} Clients.")

        # 2. ACCOUNTS
        print("Loading Accounts.")
        accounts = []
        df_acc = pd.read_csv(f'{base_path}/clean_account.csv')
        for _, row in df_acc.iterrows():
            accounts.append(Account(
                account_id=row['account_id'],
                date_created=row['date_created'],
                frequency=row['frequency']
            ))
        Account.objects.all().delete()
        Account.objects.bulk_create(accounts)
        print(f"Inserted {len(accounts)} Accounts.")

        # 3. DISPOSITIONS 
        print("Loading Dispositions.")
        disps = []
        df_disp = pd.read_csv(f'{base_path}/clean_disp.csv')
        for _, row in df_disp.iterrows():
            disps.append(Disposition(
                disp_id=row['disp_id'],
                client_id=row['client_id'],
                account_id=row['account_id'],
                type=row['type']
            ))
        Disposition.objects.all().delete()
        Disposition.objects.bulk_create(disps)
        print(f"Inserted {len(disps)} Dispositions.")

        # 4. LOANS
        print("Loading Loans.")
        loans = []
        df_loan = pd.read_csv(f'{base_path}/clean_loan.csv')
        for _, row in df_loan.iterrows():
            loans.append(Loan(
                loan_id=row['loan_id'],
                account_id=row['account_id'],
                date_granted=row['date_granted'],
                amount=row['amount'],
                duration=row['duration'],
                payments=row['payments'],
                status=row['status']
            ))
        Loan.objects.all().delete()
        Loan.objects.bulk_create(loans)
        print(f"Inserted {len(loans)} Loans.")

        # 5. TRANSACTIONS (The Big One)
        print("Loading Transactions (This might take 10-20 seconds).")
        txns = []
        df_trans = pd.read_csv(f'{base_path}/clean_trans.csv')
        
        # Batch processing to save memory
        batch_size = 50000
        total_txns = 0
        
        Transaction.objects.all().delete()

        for _, row in df_trans.iterrows():
            txns.append(Transaction(
                trans_id=row['trans_id'],
                account_id=row['account_id'],
                date=row['date'],
                type=row['type'],
                operation=row['operation'],
                amount=row['amount'],
                balance=row['balance'],
                k_symbol=row['k_symbol'],
                bank=row['bank'],
                account_partner=str(row['account']) # Store as string
            ))
            
            if len(txns) >= batch_size:
                Transaction.objects.bulk_create(txns)
                total_txns += len(txns)
                print(f"committed {total_txns} rows")
                txns = [] # Reset list

        # Commit remaining
        if txns:
            Transaction.objects.bulk_create(txns)
        print("Transaction Loaded.")        
        print(" DATABASE IS LIVE ")