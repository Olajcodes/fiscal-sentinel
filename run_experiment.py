import opik
from opik.evaluation import evaluate
from app.agent.core import run_sentinel
from app.data.mock_plaid import get_mock_transactions
from app.evaluation.metrics import LegalCitationMetric, ActionabilityMetric, ConversationMetric
import time

# Initialize Opik Client
client = opik.Opik()

# Define the Test Data
raw_data = [
    {"input": "Hi"},
    {"input": "I noticed a hidden fee from my bank. Can I fight it?"},
    {"input": "Netflix raised my price without asking. Is that legal?"},
    {"input": "I want to cancel my gym but they said I have to come in person."},
    {"input": "Are there any zombies in my subscription list?"},
    {"input": "Draft a letter to Equinox regarding my unused membership."}
]

# Get or Create the Dataset
dataset = client.get_or_create_dataset(
    name="Fiscal_Sentinel_Dataset_Week2",
    description="Test cases for Consumer Law compliance"
)

try:
    dataset.insert(raw_data)
except Exception as e:
    print(f"⚠️ Note: Dataset insertion skipped or errored (might already exist): {e}")

# Define the Evaluation Task
def eval_task(item):
    tx = get_mock_transactions()
    user_input = item["input"] 
    response = run_sentinel(user_input, tx, history=[])
    return { "output": response }

# Run the Evaluation
if __name__ == "__main__":
    # Generate a unique name using timestamp to avoid "500 Internal Server" errors
    unique_id = int(time.time())
    exp_name = f"Fiscal_Sentinel_Run_{unique_id}"
    
    print(f"🧪 Starting Opik Experiment: {exp_name}...")
    
    evaluate(
        experiment_name=exp_name,
        dataset=dataset,
        task=eval_task,
        scoring_metrics=[LegalCitationMetric(), ActionabilityMetric(), ConversationMetric()],
        task_threads=1 # Keeps it slow and steady to avoid 503 errors
    )
    
    print("\n✅ Experiment Complete! Check your Opik Dashboard.")
