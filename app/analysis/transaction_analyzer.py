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
