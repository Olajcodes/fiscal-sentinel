# Fake bank transactions for dev

from datetime import datetime, timedelta

def get_mock_transactions():
    """
    Returns a list of simulated bank transactions.
    """
    today = datetime.now()
    
    # Helper to format dates relative to "today"
    def date_days_ago(days):
        return (today - timedelta(days=days)).strftime("%Y-%m-%d")

    return [
        # TRAP 1: The Price Hike (Netflix went up $3 without notice)
        {
            "transaction_id": "tx_001",
            "date": date_days_ago(2),
            "merchant_name": "Netflix",
            "amount": 22.99,
            "category": ["Subscription", "Entertainment"],
            "notes": "Previous months were $19.99" 
        },
        # Normal Transaction
        {
            "transaction_id": "tx_002",
            "date": date_days_ago(3),
            "merchant_name": "Whole Foods Market",
            "amount": 84.50,
            "category": ["Food", "Groceries"],
            "notes": ""
        },
        # TRAP 2: The "Zombie" Subscription (User hasn't been to this gym in 4 months)
        {
            "transaction_id": "tx_003",
            "date": date_days_ago(5),
            "merchant_name": "Equinox Gym",
            "amount": 210.00,
            "category": ["Gym", "Fitness"],
            "notes": "Recurring monthly. No check-ins recorded at gym location."
        },
        # TRAP 3: The Hidden Fee
        {
            "transaction_id": "tx_004",
            "date": date_days_ago(6),
            "merchant_name": "Bank Service Fee",
            "amount": 12.00,
            "category": ["Bank Fees"],
            "notes": "Monthly Maintenance Fee"
        }
    ]