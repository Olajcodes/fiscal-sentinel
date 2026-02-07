from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional


def _parse_date(value: Any) -> Optional[datetime]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None


def _text_contains(text: str, needles: List[str]) -> bool:
    lower = text.lower()
    return any(n in lower for n in needles)


def _coerce_amount(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_amount(amount: float) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.2f}"


def _pick_extreme_transaction(
    transactions: List[Dict[str, Any]],
    prefer: str = "abs",
) -> Optional[Dict[str, Any]]:
    if not transactions:
        return None

    def amount_of(tx: Dict[str, Any]) -> float:
        return _coerce_amount(tx.get("amount", 0.0))

    candidates = []
    for tx in transactions:
        amount = amount_of(tx)
        if prefer == "debit" and amount <= 0:
            continue
        if prefer == "credit" and amount >= 0:
            continue
        candidates.append((amount, tx))

    if not candidates:
        return None

    if prefer == "credit":
        return min(candidates, key=lambda item: item[0])[1]
    if prefer == "debit":
        return max(candidates, key=lambda item: item[0])[1]
    return max(candidates, key=lambda item: abs(item[0]))[1]


def answer_transaction_query(
    user_input: str,
    transactions: List[Dict[str, Any]],
) -> Optional[str]:
    if not user_input:
        return None
    text = user_input.lower()
    extreme_words = ["highest", "largest", "biggest", "maximum", "max", "most expensive"]
    lowest_words = ["lowest", "smallest", "minimum", "min", "least expensive"]
    tx_words = [
        "transaction",
        "charge",
        "debit",
        "credit",
        "payment",
        "purchase",
        "withdrawal",
        "deposit",
        "transfer",
    ]

    wants_high = any(word in text for word in extreme_words) and any(word in text for word in tx_words)
    wants_low = any(word in text for word in lowest_words) and any(word in text for word in tx_words)
    if not (wants_high or wants_low):
        return None

    prefer = "abs"
    if any(word in text for word in ["debit", "charge", "spent", "purchase", "payment", "withdrawal", "money out", "outflow"]):
        prefer = "debit"
    elif any(word in text for word in ["credit", "deposit", "refund", "income", "money in", "inflow"]):
        prefer = "credit"

    tx = _pick_extreme_transaction(transactions, prefer=prefer)
    if not tx:
        return "I could not find any transactions to evaluate."

    amount = _coerce_amount(tx.get("amount", 0.0))
    direction = "credit" if amount < 0 else "debit"
    amount_text = _format_amount(amount)
    category = tx.get("category") or []
    if isinstance(category, list):
        category_text = ", ".join([str(c) for c in category if str(c).strip()])
    else:
        category_text = str(category)

    lines = [
        "Here is the highest transaction I found:" if wants_high else "Here is the lowest transaction I found:",
        f"- Date: {tx.get('date', '')}",
        f"- Merchant: {tx.get('merchant_name', '')}",
        f"- Amount: {amount_text} ({direction})",
    ]
    if category_text:
        lines.append(f"- Category: {category_text}")
    notes = (tx.get("notes") or "").strip()
    if notes:
        lines.append(f"- Notes: {notes}")
    tx_id = tx.get("transaction_id")
    if tx_id:
        lines.append(f"- Transaction ID: {tx_id}")
    return "\n".join(lines)


def analyze_transactions_rule_based(transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    issues: List[Dict[str, Any]] = []
    by_merchant: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for tx in transactions:
        merchant = (tx.get("merchant_name") or "Unknown Merchant").strip()
        by_merchant[merchant].append(tx)

    # Rule 1: Duplicate charges (same merchant + amount within 1 day)
    for merchant, txs in by_merchant.items():
        indexed = []
        for tx in txs:
            date = _parse_date(tx.get("date"))
            if not date:
                continue
            indexed.append((date, tx))
        indexed.sort(key=lambda x: x[0])

        for i in range(1, len(indexed)):
            prev_date, prev_tx = indexed[i - 1]
            curr_date, curr_tx = indexed[i]
            if (
                abs((curr_date - prev_date).days) <= 1
                and float(curr_tx.get("amount", 0.0)) == float(prev_tx.get("amount", 0.0))
            ):
                issues.append(
                    {
                        "merchant": merchant,
                        "issue": "Possible duplicate charge",
                        "amount": float(curr_tx.get("amount", 0.0)),
                        "reason": "Same amount charged twice within 24 hours.",
                        "needs_evidence": False,
                    }
                )
                break

    # Rule 2: Price increase for recurring subscriptions
    for merchant, txs in by_merchant.items():
        if len(txs) < 2:
            continue
        indexed = []
        for tx in txs:
            date = _parse_date(tx.get("date"))
            if not date:
                continue
            indexed.append((date, tx))
        indexed.sort(key=lambda x: x[0])
        if len(indexed) < 2:
            continue
        prev_tx = indexed[-2][1]
        curr_tx = indexed[-1][1]
        prev_amt = float(prev_tx.get("amount", 0.0))
        curr_amt = float(curr_tx.get("amount", 0.0))
        notes = (curr_tx.get("notes") or "").lower()
        category = curr_tx.get("category") or []
        category_text = " ".join(category) if isinstance(category, list) else str(category)

        if prev_amt > 0 and curr_amt > prev_amt * 1.1 and _text_contains(
            f"{notes} {category_text}", ["subscription", "recurring", "plan", "membership"]
        ):
            issues.append(
                {
                    "merchant": merchant,
                    "issue": "Possible price increase on subscription",
                    "amount": curr_amt,
                    "reason": f"Amount increased from {prev_amt:.2f} to {curr_amt:.2f}.",
                    "needs_evidence": False,
                }
            )

    # Rule 3: Cancellation friction or post-cancel billing
    for merchant, txs in by_merchant.items():
        for tx in txs:
            notes = (tx.get("notes") or "")
            if _text_contains(notes, ["cancel", "cancellation", "terminate", "in person"]):
                issues.append(
                    {
                        "merchant": merchant,
                        "issue": "Cancellation friction or billing after cancel request",
                        "amount": float(tx.get("amount", 0.0)),
                        "reason": "Notes mention cancellation or in-person requirement.",
                        "needs_evidence": False,
                    }
                )
                break

    # Rule 4: Free trial conversion without notice
    for merchant, txs in by_merchant.items():
        for tx in txs:
            notes = (tx.get("notes") or "")
            if _text_contains(notes, ["free trial", "trial ended", "trial"]):
                issues.append(
                    {
                        "merchant": merchant,
                        "issue": "Free trial converted to paid plan",
                        "amount": float(tx.get("amount", 0.0)),
                        "reason": "Charge occurred after a trial period.",
                        "needs_evidence": False,
                    }
                )
                break

    # Rule 5: Unexpected fees
    for merchant, txs in by_merchant.items():
        for tx in txs:
            category = tx.get("category") or []
            category_text = " ".join(category) if isinstance(category, list) else str(category)
            notes = (tx.get("notes") or "")
            if _text_contains(f"{merchant} {notes} {category_text}", ["fee", "fees", "maintenance"]):
                issues.append(
                    {
                        "merchant": merchant,
                        "issue": "Unexpected fee",
                        "amount": float(tx.get("amount", 0.0)),
                        "reason": "Charge categorized as a fee or described as maintenance.",
                        "needs_evidence": False,
                    }
                )
                break

    # Rule 6: Chargeback or dispute fees
    for merchant, txs in by_merchant.items():
        for tx in txs:
            notes = (tx.get("notes") or "")
            if _text_contains(notes, ["chargeback fee", "dispute fee", "returned item fee"]):
                issues.append(
                    {
                        "merchant": merchant,
                        "issue": "Possible chargeback/dispute fee",
                        "amount": float(tx.get("amount", 0.0)),
                        "reason": "Notes mention a chargeback or dispute-related fee.",
                        "needs_evidence": False,
                    }
                )
                break

    # Rule 7: Multiple same-day charges (possible split billing)
    for merchant, txs in by_merchant.items():
        by_date: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        for tx in txs:
            date = _parse_date(tx.get("date"))
            if not date:
                continue
            by_date[date.strftime("%Y-%m-%d")].append(tx)

        for day, day_txs in by_date.items():
            if len(day_txs) < 2:
                continue
            amounts = [float(tx.get("amount", 0.0)) for tx in day_txs]
            if len(set(amounts)) == 1:
                continue  # duplicates handled earlier
            total = sum(amounts)
            if total <= 0:
                continue
            issues.append(
                {
                    "merchant": merchant,
                    "issue": "Multiple same-day charges",
                    "amount": total,
                    "reason": f"{len(day_txs)} charges on {day}. Possible split billing.",
                    "needs_evidence": False,
                }
            )
            break

    return issues
