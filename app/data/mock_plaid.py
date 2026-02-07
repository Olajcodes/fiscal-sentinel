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
        },
        # SCENARIO 4: Cancellation Friction (Planet Fitness)
        {
            "transaction_id": "tx_005",
            "date": date_days_ago(8),
            "merchant_name": "Planet Fitness",
            "amount": 29.99,
            "category": ["Fitness"],
            "notes": "User attempted to cancel online; told to cancel in person."
        },
        # SCENARIO 5: Free Trial Conversion (Spotify)
        {
            "transaction_id": "tx_006",
            "date": date_days_ago(9),
            "merchant_name": "Spotify",
            "amount": 10.99,
            "category": ["Subscription"],
            "notes": "Free trial ended; user claims no reminder email."
        },
        # SCENARIO 6: Annual Auto-Renewal (Adobe)
        {
            "transaction_id": "tx_007",
            "date": date_days_ago(12),
            "merchant_name": "Adobe",
            "amount": 239.88,
            "category": ["Subscription"],
            "notes": "Annual plan auto-renewed; user expected monthly billing."
        },
        # SCENARIO 7: Double Charge (Amazon)
        {
            "transaction_id": "tx_008",
            "date": date_days_ago(13),
            "merchant_name": "Amazon Prime",
            "amount": 14.99,
            "category": ["Subscription"],
            "notes": "Two Prime charges appeared within 24 hours."
        },
        # SCENARIO 8: Undisclosed Price Increase (Spotify)
        {
            "transaction_id": "tx_009",
            "date": date_days_ago(14),
            "merchant_name": "Spotify",
            "amount": 12.99,
            "category": ["Subscription"],
            "notes": "Previous months were $9.99. No notice in inbox."
        },
        # SCENARIO 9: Service Not Used (Netflix)
        {
            "transaction_id": "tx_010",
            "date": date_days_ago(16),
            "merchant_name": "Netflix",
            "amount": 15.49,
            "category": ["Subscription"],
            "notes": "Account unused for 60 days; user wants to cancel."
        },
        # SCENARIO 10: Refund Not Received (Adobe)
        {
            "transaction_id": "tx_011",
            "date": date_days_ago(18),
            "merchant_name": "Adobe",
            "amount": 19.99,
            "category": ["Subscription"],
            "notes": "User canceled within trial; refund promised but not received."
        },
        # SCENARIO 11: Hidden Fee (Amazon)
        {
            "transaction_id": "tx_012",
            "date": date_days_ago(19),
            "merchant_name": "Amazon Marketplace Fee",
            "amount": 6.49,
            "category": ["Fees"],
            "notes": "Unexpected service fee on digital purchase."
        },
        # SCENARIO 12: Billing After Cancellation (Planet Fitness)
        {
            "transaction_id": "tx_013",
            "date": date_days_ago(21),
            "merchant_name": "Planet Fitness",
            "amount": 29.99,
            "category": ["Fitness"],
            "notes": "Charged after cancellation request was submitted."
        },
        # SCENARIO 13: Late Fee (Bank)
        {
            "transaction_id": "tx_014",
            "date": date_days_ago(25),
            "merchant_name": "Chase Bank Fee",
            "amount": 25.00,
            "category": ["Fees"],
            "notes": "Late fee applied despite on-time payment."
        },
        # SCENARIO 14: Annual Renewal Surprise (Amazon)
        {
            "transaction_id": "tx_015",
            "date": date_days_ago(30),
            "merchant_name": "Amazon Prime",
            "amount": 139.00,
            "category": ["Subscription"],
            "notes": "Annual renewal processed; user expected reminder."
        }
    ]
