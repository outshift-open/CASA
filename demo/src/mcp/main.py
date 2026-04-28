# Copyright 2026 Cisco Systems, Inc. and its affiliates
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Fictitious Banking Application - MCP Server
Run from the repository root:
    python mcp/main.py
"""

from datetime import datetime
import os

import uvicorn
from fastapi import FastAPI
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings


# In-memory banking data storage for a single customer
class BankingDataStore:
    def __init__(self):
        # Account holder information
        self.account_holder = {
            "name": "John Smith",
            "customer_id": "CUST001",
            "email": "john.smith@email.com",
            "phone": "+1-555-0123",
        }

        # Multiple accounts for different purposes, all belonging to the same person
        self.accounts = {
            "ACC001": {
                "nickname": "Primary Checking",
                "balance": 5234.67,
                "type": "checking",
                "status": "active",
                "account_number": "****1234",
            },
            "ACC002": {
                "nickname": "Emergency Savings",
                "balance": 15000.00,
                "type": "savings",
                "status": "active",
                "account_number": "****5678",
            },
            "ACC003": {
                "nickname": "Vacation Fund",
                "balance": 8750.50,
                "type": "savings",
                "status": "active",
                "account_number": "****9012",
            },
        }

        # Transaction history across all accounts
        self.transactions = [
            {
                "id": "TXN001",
                "account": "ACC001",
                "type": "deposit",
                "amount": 3200.00,
                "date": "2025-11-01",
                "description": "Paycheck deposit",
            },
            {
                "id": "TXN002",
                "account": "ACC001",
                "type": "withdrawal",
                "amount": 150.00,
                "date": "2025-11-05",
                "description": "Grocery shopping",
            },
            {
                "id": "TXN003",
                "account": "ACC002",
                "type": "deposit",
                "amount": 1000.00,
                "date": "2025-11-01",
                "description": "Monthly savings transfer",
            },
            {
                "id": "TXN004",
                "account": "ACC003",
                "type": "deposit",
                "amount": 500.00,
                "date": "2025-11-07",
                "description": "Vacation savings",
            },
            {
                "id": "TXN005",
                "account": "ACC004",
                "type": "deposit",
                "amount": 5000.00,
                "date": "2025-11-03",
                "description": "Investment contribution",
            },
            {
                "id": "TXN006",
                "account": "ACC005",
                "type": "withdrawal",
                "amount": 280.00,
                "date": "2025-11-08",
                "description": "Office supplies",
            },
            {
                "id": "TXN007",
                "account": "ACC001",
                "type": "withdrawal",
                "amount": 85.00,
                "date": "2025-11-10",
                "description": "Restaurant",
            },
        ]

        # Scheduled payments/transfers
        self.scheduled_payments = [
            {
                "id": "PAY001",
                "from_account": "ACC001",
                "to_account": "ACC002",
                "amount": 1000.00,
                "frequency": "monthly",
                "next_date": "2025-12-01",
                "description": "Monthly emergency fund",
            },
            {
                "id": "PAY002",
                "from_account": "ACC001",
                "to_account": "ACC003",
                "amount": 500.00,
                "frequency": "monthly",
                "next_date": "2025-12-01",
                "description": "Vacation savings",
            },
            {
                "id": "PAY003",
                "from_account": "ACC001",
                "payee": "Electric Company",
                "amount": 120.00,
                "frequency": "monthly",
                "next_date": "2025-11-15",
                "description": "Electricity bill",
            },
            {
                "id": "PAY004",
                "from_account": "ACC001",
                "payee": "Internet Provider",
                "amount": 80.00,
                "frequency": "monthly",
                "next_date": "2025-11-20",
                "description": "Internet service",
            },
        ]

        # Cards associated with accounts
        self.cards = {
            "ACC001": [
                {"number": "****1234", "type": "debit", "status": "active", "expiry": "12/2027"},
                {
                    "number": "****5555",
                    "type": "credit",
                    "status": "active",
                    "expiry": "08/2026",
                    "limit": 10000.00,
                    "balance": 2350.00,
                },
            ],
            "ACC005": [{"number": "****7890", "type": "debit", "status": "active", "expiry": "03/2028"}],
        }

        # External beneficiaries for payments
        self.external_beneficiaries = [
            {
                "id": "BEN001",
                "name": "Sarah Smith",
                "account": "****9999",
                "bank": "First National Bank",
                "relationship": "Sister",
            },
            {
                "id": "BEN002",
                "name": "ABC Landlord",
                "account": "****8888",
                "bank": "City Bank",
                "relationship": "Rent",
            },
        ]


# Initialize global data store
banking_data = BankingDataStore()

# Create FastMCP instance as a Resource Server
mcp = FastMCP(
    "SecureBank Digital Banking Service",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=False  # safe when behind a trusted reverse proxy
    )
)


@mcp.tool()
def get_account_summary() -> str:
    """Get a summary of all your accounts with balances."""
    holder = banking_data.account_holder
    result = f"Account Summary for {holder['name']}\n"
    result += f"Customer ID: {holder['customer_id']}\n"
    result += "=" * 70 + "\n\n"

    total_balance = 0
    for acc_id, details in banking_data.accounts.items():
        result += f"{details['nickname']} ({acc_id})\n"
        result += f"  Type: {details['type'].capitalize()} | Balance: ${details['balance']:,.2f}\n"
        result += f"  Account: {details['account_number']} | Status: {details['status']}\n\n"
        total_balance += details["balance"]

    result += "=" * 70 + "\n"
    result += f"Total Balance Across All Accounts: ${total_balance:,.2f}"

    return result


@mcp.tool()
def get_account_balance(account_id: str) -> str:
    """Get the current balance for a specific account (e.g., ACC001, ACC002)."""
    if account_id not in banking_data.accounts:
        return f"Error: Account {account_id} not found. Use get_account_summary() to see all your accounts."

    account = banking_data.accounts[account_id]
    return f"{account['nickname']} ({account_id})\nBalance: ${account['balance']:,.2f}\nType: {account['type'].capitalize()}"


@mcp.tool()
def get_transaction_history(account_id: str = None, limit: int = 10) -> str:
    """Get recent transaction history. If account_id is provided, shows transactions for that account only, otherwise shows all transactions."""
    if account_id and account_id not in banking_data.accounts:
        return f"Error: Account {account_id} not found"

    # Filter transactions
    if account_id:
        txns = [t for t in banking_data.transactions if t["account"] == account_id]
        title = f"Recent Transactions for {banking_data.accounts[account_id]['nickname']}"
    else:
        txns = banking_data.transactions
        title = "Recent Transactions (All Accounts)"

    txns.sort(key=lambda x: x["date"], reverse=True)

    if not txns:
        return "No transactions found"

    result = title + "\n" + "=" * 70 + "\n"
    for txn in txns[:limit]:
        acc_name = banking_data.accounts[txn["account"]]["nickname"]
        result += f"{txn['date']} | {txn['type'].upper()} | ${txn['amount']:,.2f}\n"
        result += f"  {acc_name} - {txn['description']} (ID: {txn['id']})\n"

    return result


@mcp.tool()
def transfer_between_accounts(
    from_account: str, to_account: str, amount: float, description: str = "Internal transfer"
) -> str:
    """Transfer money between your own accounts."""
    # Validation
    if from_account not in banking_data.accounts:
        return f"Error: Source account {from_account} not found"
    if to_account not in banking_data.accounts:
        return f"Error: Destination account {to_account} not found"
    if from_account == to_account:
        return "Error: Cannot transfer to the same account"
    if amount <= 0:
        return "Error: Transfer amount must be positive"
    if banking_data.accounts[from_account]["balance"] < amount:
        return f"Error: Insufficient funds in {banking_data.accounts[from_account]['nickname']}. Available: ${banking_data.accounts[from_account]['balance']:,.2f}"

    # Perform transfer
    banking_data.accounts[from_account]["balance"] -= amount
    banking_data.accounts[to_account]["balance"] += amount

    # Record transactions
    today = datetime.now().strftime("%Y-%m-%d")
    txn_id = f"TXN{len(banking_data.transactions) + 1:03d}"

    banking_data.transactions.append(
        {
            "id": txn_id,
            "account": from_account,
            "type": "transfer_out",
            "amount": amount,
            "date": today,
            "description": f"{description} to {banking_data.accounts[to_account]['nickname']}",
        }
    )

    banking_data.transactions.append(
        {
            "id": f"TXN{len(banking_data.transactions) + 1:03d}",
            "account": to_account,
            "type": "transfer_in",
            "amount": amount,
            "date": today,
            "description": f"{description} from {banking_data.accounts[from_account]['nickname']}",
        }
    )

    from_acc = banking_data.accounts[from_account]
    to_acc = banking_data.accounts[to_account]

    return (
        "✓ Transfer Complete\n"
        + "=" * 70
        + f"\nTransferred ${amount:,.2f}\nFrom: {from_acc['nickname']} (New balance: ${from_acc['balance']:,.2f})\nTo: {to_acc['nickname']} (New balance: ${to_acc['balance']:,.2f})"
    )


@mcp.tool()
def deposit_funds(account_id: str, amount: float, description: str = "Deposit") -> str:
    """Deposit money into one of your accounts."""
    if account_id not in banking_data.accounts:
        return f"Error: Account {account_id} not found"
    if amount <= 0:
        return "Error: Deposit amount must be positive"

    # Update balance
    banking_data.accounts[account_id]["balance"] += amount

    # Record transaction
    today = datetime.now().strftime("%Y-%m-%d")
    txn_id = f"TXN{len(banking_data.transactions) + 1:03d}"

    banking_data.transactions.append(
        {
            "id": txn_id,
            "account": account_id,
            "type": "deposit",
            "amount": amount,
            "date": today,
            "description": description,
        }
    )

    account = banking_data.accounts[account_id]
    return (
        "✓ Deposit Complete\n"
        + "=" * 70
        + f"\nDeposited ${amount:,.2f} to {account['nickname']}\nNew Balance: ${account['balance']:,.2f}"
    )


@mcp.tool()
def withdraw_funds(account_id: str, amount: float, description: str = "Withdrawal") -> str:
    """Withdraw money from one of your accounts."""
    if account_id not in banking_data.accounts:
        return f"Error: Account {account_id} not found"
    if amount <= 0:
        return "Error: Withdrawal amount must be positive"
    if banking_data.accounts[account_id]["balance"] < amount:
        return f"Error: Insufficient funds. Available: ${banking_data.accounts[account_id]['balance']:,.2f}"

    # Update balance
    banking_data.accounts[account_id]["balance"] -= amount

    # Record transaction
    today = datetime.now().strftime("%Y-%m-%d")
    txn_id = f"TXN{len(banking_data.transactions) + 1:03d}"

    banking_data.transactions.append(
        {
            "id": txn_id,
            "account": account_id,
            "type": "withdrawal",
            "amount": amount,
            "date": today,
            "description": description,
        }
    )

    account = banking_data.accounts[account_id]
    return (
        "✓ Withdrawal Complete\n"
        + "=" * 70
        + f"\nWithdrew ${amount:,.2f} from {account['nickname']}\nNew Balance: ${account['balance']:,.2f}"
    )


@mcp.tool()
def get_scheduled_payments() -> str:
    """View all your scheduled payments and automatic transfers."""
    if not banking_data.scheduled_payments:
        return "No scheduled payments found"

    result = "Your Scheduled Payments\n" + "=" * 70 + "\n"

    for payment in banking_data.scheduled_payments:
        from_acc = banking_data.accounts.get(payment["from_account"], {}).get("nickname", "Unknown")

        if "to_account" in payment:
            # Internal transfer
            to_acc = banking_data.accounts.get(payment["to_account"], {}).get("nickname", "Unknown")
            result += f"ID: {payment['id']} | INTERNAL TRANSFER\n"
            result += f"  From: {from_acc} → To: {to_acc}\n"
        else:
            # External payment
            result += f"ID: {payment['id']} | BILL PAYMENT\n"
            result += f"  From: {from_acc} → Payee: {payment['payee']}\n"

        result += f"  Amount: ${payment['amount']:,.2f} | Frequency: {payment['frequency']}\n"
        result += f"  Next Payment: {payment['next_date']} | {payment['description']}\n\n"

    return result


@mcp.tool()
def get_card_details() -> str:
    """View all your debit and credit cards."""
    result = "Your Cards\n" + "=" * 70 + "\n"

    for acc_id, cards in banking_data.cards.items():
        acc_name = banking_data.accounts[acc_id]["nickname"]
        result += f"\n{acc_name} ({acc_id}):\n"

        for card in cards:
            result += f"  • {card['type'].upper()} Card {card['number']}\n"
            result += f"    Status: {card['status']} | Expires: {card['expiry']}\n"
            if card["type"] == "credit":
                available = card["limit"] - card["balance"]
                result += (
                    f"    Limit: ${card['limit']:,.2f} | Used: ${card['balance']:,.2f} | Available: ${available:,.2f}\n"
                )

    return result


@mcp.tool()
def get_external_beneficiaries() -> str:
    """View your saved external beneficiaries for payments and transfers."""
    if not banking_data.external_beneficiaries:
        return "No external beneficiaries registered"

    result = "Your External Beneficiaries\n" + "=" * 70 + "\n"

    for ben in banking_data.external_beneficiaries:
        result += f"ID: {ben['id']} | {ben['name']}\n"
        result += f"  Account: {ben['account']} at {ben['bank']}\n"
        result += f"  Relationship: {ben['relationship']}\n\n"

    return result


@mcp.tool()
def add_external_beneficiary(name: str, account_number: str, bank_name: str, relationship: str = "Other") -> str:
    """Add a new external beneficiary for future payments and transfers."""
    if not name or not account_number or not bank_name:
        return "Error: Name, account number, and bank name are required"

    # Generate new beneficiary ID
    ben_id = f"BEN{len(banking_data.external_beneficiaries) + 1:03d}"

    # Mask account number for security (show only last 4 digits)
    if len(account_number) > 4:
        masked_account = "****" + account_number[-4:]
    else:
        masked_account = account_number

    # Add new beneficiary
    new_beneficiary = {
        "id": ben_id,
        "name": name,
        "account": masked_account,
        "bank": bank_name,
        "relationship": relationship,
    }

    banking_data.external_beneficiaries.append(new_beneficiary)

    result = "✓ Beneficiary Added Successfully\n" + "=" * 70 + "\n"
    result += f"ID: {ben_id}\n"
    result += f"Name: {name}\n"
    result += f"Account: {masked_account} at {bank_name}\n"
    result += f"Relationship: {relationship}\n\n"
    result += f"Total beneficiaries: {len(banking_data.external_beneficiaries)}"

    return result


@mcp.tool()
def schedule_payment(
    from_account: str,
    amount: float,
    frequency: str,
    next_date: str,
    payee: str = None,
    to_account: str = None,
    description: str = "Scheduled payment",
) -> str:
    """Schedule a new recurring payment or transfer.

    For internal transfers: provide from_account, to_account, amount, frequency, next_date
    For external payments: provide from_account, payee, amount, frequency, next_date

    frequency options: 'weekly', 'biweekly', 'monthly', 'quarterly', 'annually'
    next_date format: YYYY-MM-DD (e.g., 2025-12-01)
    """
    # Validation
    if from_account not in banking_data.accounts:
        return f"Error: Account {from_account} not found"

    if not payee and not to_account:
        return "Error: Must specify either payee (for external payment) or to_account (for internal transfer)"

    if payee and to_account:
        return "Error: Cannot specify both payee and to_account. Choose one."

    if to_account and to_account not in banking_data.accounts:
        return f"Error: Destination account {to_account} not found"

    if amount <= 0:
        return "Error: Payment amount must be positive"

    valid_frequencies = ["weekly", "biweekly", "monthly", "quarterly", "annually"]
    if frequency.lower() not in valid_frequencies:
        return f"Error: Invalid frequency. Must be one of: {', '.join(valid_frequencies)}"

    # Validate date format
    try:
        datetime.strptime(next_date, "%Y-%m-%d")
    except ValueError:
        return "Error: Invalid date format. Use YYYY-MM-DD (e.g., 2025-12-01)"

    # Generate new payment ID
    pay_id = f"PAY{len(banking_data.scheduled_payments) + 1:03d}"

    # Create new scheduled payment
    new_payment = {
        "id": pay_id,
        "from_account": from_account,
        "amount": amount,
        "frequency": frequency.lower(),
        "next_date": next_date,
        "description": description,
    }

    if to_account:
        new_payment["to_account"] = to_account
        payment_type = "INTERNAL TRANSFER"
        destination = banking_data.accounts[to_account]["nickname"]
    else:
        new_payment["payee"] = payee
        payment_type = "BILL PAYMENT"
        destination = payee

    banking_data.scheduled_payments.append(new_payment)

    from_acc_name = banking_data.accounts[from_account]["nickname"]

    result = "✓ Payment Scheduled Successfully\n" + "=" * 70 + "\n"
    result += f"Payment ID: {pay_id}\n"
    result += f"Type: {payment_type}\n"
    result += f"From: {from_acc_name} ({from_account})\n"
    result += f"To: {destination}\n"
    result += f"Amount: ${amount:,.2f}\n"
    result += f"Frequency: {frequency.capitalize()}\n"
    result += f"Next Payment: {next_date}\n"
    result += f"Description: {description}\n\n"
    result += f"Total scheduled payments: {len(banking_data.scheduled_payments)}"

    return result


@mcp.tool()
def calculate_savings_goal(target_amount: float, monthly_contribution: float, current_savings: float = 0) -> str:
    """Calculate how long it will take to reach a savings goal."""
    if target_amount <= 0 or monthly_contribution <= 0:
        return "Error: Target amount and monthly contribution must be positive"

    if current_savings >= target_amount:
        return f"You've already reached your goal! Current savings: ${current_savings:,.2f}"

    remaining = target_amount - current_savings
    months_needed = remaining / monthly_contribution
    years = int(months_needed // 12)
    months = int(months_needed % 12)

    result = "Savings Goal Calculator\n" + "=" * 70 + "\n"
    result += f"Target Amount: ${target_amount:,.2f}\n"
    result += f"Current Savings: ${current_savings:,.2f}\n"
    result += f"Amount Needed: ${remaining:,.2f}\n"
    result += f"Monthly Contribution: ${monthly_contribution:,.2f}\n"
    result += "\nTime to Goal: "

    if years > 0:
        result += f"{years} year{'s' if years != 1 else ''} and "
    result += f"{months} month{'s' if months != 1 else ''}\n"
    result += f"(approximately {months_needed:.1f} months total)"

    return result


app = FastAPI(
    title="SecureBank Digital Banking API",
    description="Fictitious banking application with account management, transactions, and payment services",
    lifespan=lambda _: mcp.session_manager.run(),
)

app.mount("/", mcp.streamable_http_app())

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("🏦  SecureBank Digital Banking Service Starting...")
    print("=" * 70)
    print("Server: http://0.0.0.0:3000")
    print(f"Accounts initialized: {len(banking_data.accounts)}")
    print(f"Total deposits: ${sum(acc['balance'] for acc in banking_data.accounts.values()):,.2f}")
    print("=" * 70 + "\n")
    uvicorn_loop = os.environ.get("UVICORN_LOOP", "uvloop")
    print(f"[boot] UVICORN_LOOP={uvicorn_loop}", flush=True)
    uvicorn.run(app, host="0.0.0.0", port=3000, loop=uvicorn_loop)
