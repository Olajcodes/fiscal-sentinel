from app.data.mock_plaid import get_mock_transactions
from app.agent.core import run_sentinel
import os

def test_system():
    # 1. Load Data
    print("--- 1. LOADING MOCK TRANSACTIONS ---")
    transactions = get_mock_transactions()
    print(f"Loaded {len(transactions)} transactions.\n")

    # 2. Run Agent
    print("--- 2. WAKING UP SENTINEL ---")
    user_query = "Scan my transactions. Are there any bogus fees or subscriptions I should kill?"
    
    response = run_sentinel(user_query, transactions)

    # 3. Output
    print("\n--- 3. AGENT RESPONSE ---")
    print(response)
    
    # 4. Opik Reminder
    if os.environ.get("OPIK_API_KEY"):
        print("\n✅ Trace logged to Opik! Check your dashboard.")
    else:
        print("\n⚠️ Opik API Key not found. Trace might be local only.")

if __name__ == "__main__":
    test_system()