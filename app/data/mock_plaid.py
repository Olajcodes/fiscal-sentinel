# Fake bank transactions for dev

from datetime import datetime, timedelta

def get_mock_transactions():
    """
    Returns simulated bank transactions designed to trigger the Agent.
    """
    today = datetime.now()
    
    def date_days_ago(days):
        return (today - timedelta(days=days)).strftime("%Y-%m-%d")

    return [
        # SCENARIO 1: Illegal Price Hike (Netflix)
        {
            "transaction_id": "tx_001",
            "date": date_days_ago(2),
            "merchant_name": "Netflix",
            "amount": 22.99,
            "category": ["Subscription"],
            "notes": "Previous months were $19.99. No notification email found." 
        },
        # SCENARIO 2: Zombie Subscription (Equinox)
        {
            "transaction_id": "tx_003",
            "date": date_days_ago(5),
            "merchant_name": "Equinox Gym",
            "amount": 210.00,
            "category": ["Fitness"],
            "notes": "Recurring monthly. User location data shows 0 visits in 90 days."
        },
        # SCENARIO 3: Junk Fee
        {
            "transaction_id": "tx_004",
            "date": date_days_ago(6),
            "merchant_name": "Chase Bank Fee",
            "amount": 12.00,
            "category": ["Fees"],
            "notes": "Monthly Maintenance Fee"
        }
    ]