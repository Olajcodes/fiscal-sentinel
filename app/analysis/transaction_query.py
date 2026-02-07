from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple
from collections import Counter
import os
import re

from app.analysis.transaction_analyzer import analyze_transactions_rule_based

TX_KEYWORDS = [
    "transaction",
    "transactions",
    "charge",
    "charges",
    "debit",
    "credit",
    "payment",
    "purchase",
    "withdrawal",
    "deposit",
    "transfer",
    "spend",
    "spent",
    "fee",
    "fees",
    "subscription",
    "recurring",
]

DEBIT_WORDS = [
    "debit",
    "charge",
    "spent",
    "spend",
    "purchase",
    "payment",
    "withdrawal",
    "money out",
    "outflow",
    "fee",
]

CREDIT_WORDS = [
    "credit",
    "deposit",
    "refund",
    "income",
    "money in",
    "inflow",
]

MAX_WORDS = ["highest", "largest", "biggest", "maximum", "max", "most expensive"]
MIN_WORDS = ["lowest", "smallest", "minimum", "min", "least expensive"]


@dataclass
class TransactionQuery:
    query_type: str
    direction: str = "any"
    merchant: Optional[str] = None
    category: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    needs_followup: bool = False
    follow_up_question: Optional[str] = None


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _parse_date_str(value: str) -> Optional[date]:
    text = value.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _extract_dates(text: str) -> List[date]:
    dates: List[date] = []
    patterns = [
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}/\d{1,2}/\d{2,4}\b",
    ]
    for pattern in patterns:
        for match in re.findall(pattern, text):
            parsed = _parse_date_str(match)
            if parsed:
                dates.append(parsed)
    return dates


def _parse_date_range(text: str) -> Tuple[Optional[date], Optional[date]]:
    today = datetime.utcnow().date()

    match = re.search(r"\b(last|past)\s+(\d{1,3})\s+days\b", text)
    if match:
        days = int(match.group(2))
        return today - timedelta(days=days), today

    if "last week" in text:
        return today - timedelta(days=7), today
    if "this week" in text:
        return today - timedelta(days=today.weekday()), today

    if "last month" in text:
        first_this_month = today.replace(day=1)
        last_month_end = first_this_month - timedelta(days=1)
        return last_month_end.replace(day=1), last_month_end
    if "this month" in text:
        return today.replace(day=1), today

    if "yesterday" in text:
        day = today - timedelta(days=1)
        return day, day
    if "today" in text:
        return today, today

    dates = _extract_dates(text)
    if len(dates) >= 2 and ("from" in text or "between" in text or "to" in text):
        start, end = sorted(dates[:2])
        return start, end
    if len(dates) == 1 and any(k in text for k in ["on", "for", "during", "date"]):
        return dates[0], dates[0]

    return None, None


def _extract_merchants(transactions: List[Dict[str, Any]]) -> List[str]:
    names = set()
    for tx in transactions:
        name = str(tx.get("merchant_name") or "").strip()
        if name:
            names.add(name)
    return sorted(names, key=lambda n: len(n), reverse=True)


def _extract_categories(transactions: List[Dict[str, Any]]) -> List[str]:
    categories = set()
    for tx in transactions:
        cat = tx.get("category") or []
        if isinstance(cat, list):
            for item in cat:
                item_text = str(item).strip()
                if item_text:
                    categories.add(item_text)
        else:
            item_text = str(cat).strip()
            if item_text:
                categories.add(item_text)
    return sorted(categories, key=lambda n: len(n), reverse=True)


def _match_from_list(text: str, candidates: List[str]) -> Optional[str]:
    for candidate in candidates:
        if candidate.lower() in text:
            return candidate
    return None


def _detect_direction(text: str) -> str:
    if any(word in text for word in DEBIT_WORDS):
        return "debit"
    if any(word in text for word in CREDIT_WORDS):
        return "credit"
    return "any"


def _detect_query_type(text: str) -> Optional[str]:
    if any(word in text for word in MAX_WORDS):
        return "max"
    if any(word in text for word in MIN_WORDS):
        return "min"
    if "how many" in text or "count" in text or "number of" in text:
        return "count"
    if "by category" in text or "category breakdown" in text or "per category" in text:
        return "by_category"
    if "by merchant" in text or "merchant breakdown" in text or "per merchant" in text or "top merchant" in text:
        return "by_merchant"
    if any(word in text for word in ["total", "sum", "how much"]):
        return "total"
    if any(word in text for word in ["spent", "spend", "paid", "income"]):
        return "total"
    if any(word in text for word in ["recent", "latest", "most recent", "last transaction"]):
        return "recent"
    if "subscription" in text or "recurring" in text:
        return "subscription_scan"
    return None


def _needs_followup(text: str, merchant: Optional[str], date_range: Tuple[Optional[date], Optional[date]]) -> bool:
    if merchant or any(date_range):
        return False
    ambiguous = [
        "is this charge",
        "is that charge",
        "is this transaction",
        "is that transaction",
        "is this legit",
        "is that legit",
        "this charge",
        "that charge",
        "this transaction",
        "that transaction",
    ]
    return any(phrase in text for phrase in ambiguous)


def parse_transaction_query(text: str, transactions: List[Dict[str, Any]]) -> Optional[TransactionQuery]:
    if not text:
        return None
    normalized = _normalize(text)
    query_type = _detect_query_type(normalized)
    if query_type is None and not any(k in normalized for k in TX_KEYWORDS):
        return None

    merchant = _match_from_list(normalized, _extract_merchants(transactions))
    category = _match_from_list(normalized, _extract_categories(transactions))
    direction = _detect_direction(normalized)
    start_date, end_date = _parse_date_range(normalized)

    needs_followup = _needs_followup(normalized, merchant, (start_date, end_date))
    follow_up = None
    if needs_followup:
        follow_up = "Which transaction should I check (merchant, date, and amount)?"

    return TransactionQuery(
        query_type=query_type or "clarify",
        direction=direction,
        merchant=merchant,
        category=category,
        start_date=start_date,
        end_date=end_date,
        needs_followup=needs_followup,
        follow_up_question=follow_up,
    )


def _parse_tx_date(value: Any) -> Optional[date]:
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            continue
    return None


def _coerce_amount(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _format_amount(amount: float, symbol: str) -> str:
    sign = "-" if amount < 0 else ""
    return f"{sign}{symbol}{abs(amount):,.2f}"


def _symbol_from_code(code: str) -> str:
    mapping = {
        "NGN": "₦",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }
    return mapping.get(code.upper(), "")


def _resolve_currency_symbol(transactions: List[Dict[str, Any]]) -> str:
    symbols = []
    codes = []
    for tx in transactions:
        symbol = str(tx.get("currency_symbol") or "").strip()
        code = str(tx.get("currency") or "").strip()
        if symbol:
            symbols.append(symbol)
        if code:
            codes.append(code)

    if symbols:
        return Counter(symbols).most_common(1)[0][0]
    if codes:
        code = Counter(codes).most_common(1)[0][0]
        symbol = _symbol_from_code(code)
        if symbol:
            return symbol

    env_symbol = os.environ.get("DEFAULT_CURRENCY_SYMBOL", "").strip()
    if env_symbol:
        return env_symbol
    env_code = os.environ.get("DEFAULT_CURRENCY", "").strip()
    if env_code:
        symbol = _symbol_from_code(env_code)
        if symbol:
            return symbol
    return "$"


def _filter_transactions(query: TransactionQuery, transactions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    filtered: List[Dict[str, Any]] = []
    for tx in transactions:
        amount = _coerce_amount(tx.get("amount", 0.0))
        if query.direction == "debit" and amount <= 0:
            continue
        if query.direction == "credit" and amount >= 0:
            continue

        if query.merchant:
            merchant = str(tx.get("merchant_name") or "").lower()
            if query.merchant.lower() not in merchant:
                continue

        if query.category:
            categories = tx.get("category") or []
            if isinstance(categories, list):
                cat_text = " ".join(str(c).lower() for c in categories)
            else:
                cat_text = str(categories).lower()
            if query.category.lower() not in cat_text:
                continue

        if query.start_date or query.end_date:
            tx_date = _parse_tx_date(tx.get("date"))
            if not tx_date:
                continue
            if query.start_date and tx_date < query.start_date:
                continue
            if query.end_date and tx_date > query.end_date:
                continue

        filtered.append(tx)

    return filtered


def _format_tx(tx: Dict[str, Any], amount: float, symbol: str) -> List[str]:
    category = tx.get("category") or []
    if isinstance(category, list):
        category_text = ", ".join([str(c) for c in category if str(c).strip()])
    else:
        category_text = str(category)

    direction = "credit" if amount < 0 else "debit"
    lines = [
        f"- Date: {tx.get('date', '')}",
        f"- Merchant: {tx.get('merchant_name', '')}",
        f"- Amount: {_format_amount(amount, symbol)} ({direction})",
    ]
    if category_text:
        lines.append(f"- Category: {category_text}")
    notes = (tx.get("notes") or "").strip()
    if notes:
        lines.append(f"- Notes: {notes}")
    tx_id = tx.get("transaction_id")
    if tx_id:
        lines.append(f"- Transaction ID: {tx_id}")
    return lines


def answer_transaction_query(query: TransactionQuery, transactions: List[Dict[str, Any]]) -> str:
    if query.needs_followup and query.follow_up_question:
        return query.follow_up_question

    filtered = _filter_transactions(query, transactions)
    if not filtered:
        return "I could not find any transactions that match that request."
    symbol = _resolve_currency_symbol(transactions)

    if query.query_type == "max":
        chosen = max(filtered, key=lambda tx: abs(_coerce_amount(tx.get("amount", 0.0))))
        amount = _coerce_amount(chosen.get("amount", 0.0))
        header = "Here is the highest transaction I found:"
        return "\n".join([header] + _format_tx(chosen, amount, symbol))

    if query.query_type == "min":
        chosen = min(filtered, key=lambda tx: abs(_coerce_amount(tx.get("amount", 0.0))))
        amount = _coerce_amount(chosen.get("amount", 0.0))
        header = "Here is the lowest transaction I found:"
        return "\n".join([header] + _format_tx(chosen, amount, symbol))

    if query.query_type == "count":
        return f"I found {len(filtered)} transactions that match that request."

    if query.query_type == "total":
        if query.direction == "debit":
            total = sum(_coerce_amount(tx.get("amount", 0.0)) for tx in filtered if _coerce_amount(tx.get("amount", 0.0)) > 0)
            return f"Total debits: {_format_amount(total, symbol)} across {len(filtered)} transactions."
        if query.direction == "credit":
            total = sum(abs(_coerce_amount(tx.get("amount", 0.0))) for tx in filtered if _coerce_amount(tx.get("amount", 0.0)) < 0)
            return f"Total credits: {_format_amount(total, symbol)} across {len(filtered)} transactions."

        outflow = sum(_coerce_amount(tx.get("amount", 0.0)) for tx in filtered if _coerce_amount(tx.get("amount", 0.0)) > 0)
        inflow = sum(abs(_coerce_amount(tx.get("amount", 0.0))) for tx in filtered if _coerce_amount(tx.get("amount", 0.0)) < 0)
        net = sum(_coerce_amount(tx.get("amount", 0.0)) for tx in filtered)
        return (
            f"Totals for the selected transactions:\n"
            f"- Outflow: {_format_amount(outflow, symbol)}\n"
            f"- Inflow: {_format_amount(inflow, symbol)}\n"
            f"- Net: {_format_amount(net, symbol)}"
        )

    if query.query_type == "by_merchant":
        totals: Dict[str, float] = {}
        for tx in filtered:
            merchant = str(tx.get("merchant_name") or "Unknown Merchant")
            amount = _coerce_amount(tx.get("amount", 0.0))
            if query.direction == "credit":
                amount = abs(amount) if amount < 0 else 0.0
            elif query.direction == "debit":
                amount = amount if amount > 0 else 0.0
            else:
                amount = amount if amount > 0 else 0.0
            totals[merchant] = totals.get(merchant, 0.0) + amount
        top = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:5]
        lines = ["Top merchants by spend:"]
        for merchant, total in top:
            lines.append(f"- {merchant}: {_format_amount(total, symbol)}")
        return "\n".join(lines)

    if query.query_type == "by_category":
        totals: Dict[str, float] = {}
        for tx in filtered:
            categories = tx.get("category") or ["Uncategorized"]
            if not categories:
                categories = ["Uncategorized"]
            amount = _coerce_amount(tx.get("amount", 0.0))
            if query.direction == "credit":
                amount = abs(amount) if amount < 0 else 0.0
            elif query.direction == "debit":
                amount = amount if amount > 0 else 0.0
            else:
                amount = amount if amount > 0 else 0.0
            for category in categories if isinstance(categories, list) else [categories]:
                cat_key = str(category)
                totals[cat_key] = totals.get(cat_key, 0.0) + amount
        top = sorted(totals.items(), key=lambda item: item[1], reverse=True)[:5]
        lines = ["Top categories by spend:"]
        for category, total in top:
            lines.append(f"- {category}: {_format_amount(total, symbol)}")
        return "\n".join(lines)

    if query.query_type == "recent":
        def sort_key(tx: Dict[str, Any]) -> Tuple[int, date]:
            parsed = _parse_tx_date(tx.get("date"))
            return (0, parsed) if parsed else (1, date.min)

        ordered = sorted(filtered, key=sort_key, reverse=True)[:5]
        lines = ["Most recent transactions:"]
        for tx in ordered:
            amount = _coerce_amount(tx.get("amount", 0.0))
            lines.append(f"- {tx.get('date', '')} | {tx.get('merchant_name', '')} | {_format_amount(amount, symbol)}")
        return "\n".join(lines)

    if query.query_type == "subscription_scan":
        issues = analyze_transactions_rule_based(filtered)
        if not issues:
            return "I did not find any obvious subscription issues in the selected transactions."
        lines = ["Subscription-related findings:"]
        for issue in issues[:5]:
            lines.append(
                f"- {issue.get('merchant', '')}: {issue.get('issue', '')} ({_format_amount(issue.get('amount', 0.0), symbol)})"
            )
        return "\n".join(lines)

    return "Can you clarify what you want to know about your transactions?"
