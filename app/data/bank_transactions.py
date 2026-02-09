from __future__ import annotations

import csv
import io
import io
import json
import uuid
import tempfile
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

DATA_DIR = Path(__file__).resolve().parent
STORE_PATH = DATA_DIR / "bank_transactions.json"


def _parse_amount(value: Any) -> float:
    if value is None:
        return 0.0
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip().replace(",", "").replace("$", "")
    text = re.sub(r"[^\d\.\-\(\)]", "", text)
    negative = False
    if text.startswith("(") and text.endswith(")"):
        negative = True
        text = text[1:-1]
    if text.startswith("-"):
        negative = True
        text = text[1:]
    try:
        amount = float(text)
    except ValueError:
        amount = 0.0
    return -amount if negative else amount


def _symbol_from_code(code: str) -> str:
    mapping = {
        "NGN": "₦",
        "USD": "$",
        "EUR": "€",
        "GBP": "£",
    }
    return mapping.get(code.upper(), "")


def _detect_currency(record: Dict[str, Any]) -> tuple[str, str]:
    for key in ["currency", "currency_code", "iso_currency_code", "iso_currency"]:
        value = record.get(key)
        if value:
            code = str(value).strip().upper()
            return code, _symbol_from_code(code)

    for key in ["amount", "transaction_amount", "amt", "value", "debit", "credit"]:
        raw = record.get(key)
        if isinstance(raw, str):
            upper = raw.upper()
            if "₦" in raw or "NGN" in upper:
                return "NGN", "₦"
            if "$" in raw or "USD" in upper:
                return "USD", "$"
            if "€" in raw or "EUR" in upper:
                return "EUR", "€"
            if "£" in raw or "GBP" in upper:
                return "GBP", "£"

    default_code = os.environ.get("DEFAULT_CURRENCY", "").strip().upper()
    default_symbol = os.environ.get("DEFAULT_CURRENCY_SYMBOL", "").strip()
    if default_code:
        return default_code, default_symbol or _symbol_from_code(default_code)
    if default_symbol:
        return "", default_symbol
    return "", ""


def _decode_text(content: bytes) -> str:
    if not content:
        return ""
    try:
        return content.decode("utf-8-sig")
    except UnicodeDecodeError:
        return content.decode("utf-8", errors="ignore")


def _parse_date(value: Any) -> str:
    if not value:
        return ""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d")
    text = str(value).strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m/%d/%y", "%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y"):
        try:
            return datetime.strptime(text, fmt).strftime("%Y-%m-%d")
        except ValueError:
            continue
    return text[:10]


def _parse_statement_date(text: str) -> str:
    if not text:
        return ""
    tokens = (
        text.replace("\n", " ")
        .replace("\t", " ")
        .replace("\r", " ")
        .split()
    )
    for token in tokens:
        parsed = _parse_date(token)
        if parsed and len(parsed) >= 8:
            return parsed
    return _parse_date(text)


def _lower_keys(record: Dict[str, Any]) -> Dict[str, Any]:
    return {str(k).strip().lower(): v for k, v in record.items()}


def _first_value(record: Dict[str, Any], keys: List[str]) -> Optional[Any]:
    for key in keys:
        if key in record and record[key] not in (None, ""):
            return record[key]
    return None


def _normalize_category(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value)
    if ">" in text:
        parts = [p.strip() for p in text.split(">")]
        return [p for p in parts if p]
    if "," in text:
        parts = [p.strip() for p in text.split(",")]
        return [p for p in parts if p]
    return [text.strip()] if text.strip() else []


def normalize_transactions(records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    normalized: List[Dict[str, Any]] = []
    for record in records:
        rec = _lower_keys(record)
        merchant = _first_value(
            rec,
            [
                "merchant_name",
                "merchant",
                "name",
                "description",
                "payee",
            ],
        )
        notes = _first_value(rec, ["notes", "memo", "details", "note"])
        if not notes and "description" in rec and rec.get("description") != merchant:
            notes = rec.get("description")

        tx_id = _first_value(rec, ["transaction_id", "id", "txid", "reference"])
        if not tx_id:
            tx_id = f"tx_{uuid.uuid4().hex[:10]}"

        date = _parse_date(_first_value(rec, ["date", "transaction_date", "posted_date", "post_date"]))
        amount = _parse_amount(_first_value(rec, ["amount", "transaction_amount", "amt", "value", "debit", "credit"]))
        category = _normalize_category(_first_value(rec, ["category", "categories", "type"]))
        currency_code, currency_symbol = _detect_currency(rec)

        normalized.append(
            {
                "transaction_id": str(tx_id),
                "date": date,
                "merchant_name": str(merchant or "Unknown Merchant").strip(),
                "amount": amount,
                "category": category,
                "notes": str(notes or "").strip(),
                "currency": currency_code or None,
                "currency_symbol": currency_symbol or None,
            }
        )
    return normalized


DATE_RE = re.compile(r"\b\d{2}[/-]\d{2}[/-]\d{2,4}\b")
TIME_RE = re.compile(r"\b\d{1,2}:\d{2}(?::\d{2})?\b")
AMOUNT_RE = re.compile(r"(?:₦|N)?\s?\d{1,3}(?:,\d{3})*(?:\.\d{2})?")
PARTY_SLASH_RE = re.compile(r"([A-Za-z][A-Za-z .'-]{2,})/\d{6,}")


def _normalize_cell(text: str) -> str:
    return " ".join(str(text or "").lower().strip().split())


def _header_map(row: List[str]) -> Optional[Dict[str, int]]:
    indices: Dict[str, int] = {}
    for idx, cell in enumerate(row):
        norm = _normalize_cell(cell)
        if "date" in norm and "time" in norm:
            indices["datetime"] = idx
        elif "money in" in norm or "credit" in norm:
            indices["money_in"] = idx
        elif "money out" in norm or "debit" in norm:
            indices["money_out"] = idx
        elif "category" in norm:
            indices["category"] = idx
        elif "to" in norm and "from" in norm:
            indices["party"] = idx
        elif "description" in norm:
            indices["description"] = idx
        elif "balance" in norm:
            indices["balance"] = idx
    if "datetime" in indices and ("money_in" in indices or "money_out" in indices):
        return indices
    return None


def _looks_like_header(row_text: str) -> bool:
    norm = _normalize_cell(row_text)
    return any(
        key in norm
        for key in [
            "account number",
            "opening balance",
            "closing balance",
            "summary",
            "page",
            "money in",
            "money out",
            "date/time",
        ]
    )


def _guess_category(text: str) -> List[str]:
    lower = text.lower()
    if "transfer" in lower:
        return ["Transfer"]
    if "withdrawal" in lower:
        return ["Withdrawal"]
    if "fee" in lower or "stamp duty" in lower:
        return ["Fees"]
    if "payment" in lower:
        return ["Payment"]
    return []


def _extract_party(text: str) -> str:
    slash_match = PARTY_SLASH_RE.search(text)
    if slash_match:
        return slash_match.group(1).strip()
    lower = text.lower()
    markers = ["transfer", "payment", "withdrawal"]
    for marker in markers:
        if marker in lower:
            start = lower.index(marker) + len(marker)
            segment = text[start:]
            segment = DATE_RE.sub("", segment)
            segment = TIME_RE.sub("", segment)
            segment = AMOUNT_RE.sub("", segment)
            segment = re.sub(
                r"\b(inward|outward|transfer|payment|withdrawal|stamp|duty|balance)\b",
                " ",
                segment,
                flags=re.IGNORECASE,
            )
            tokens = [t for t in segment.split() if len(t) > 1]
            if tokens:
                return " ".join(tokens[:6])
    # Fallback: strip numeric tokens and take the first few words.
    segment = DATE_RE.sub("", text)
    segment = TIME_RE.sub("", segment)
    segment = AMOUNT_RE.sub("", segment)
    tokens = [t for t in segment.split() if len(t) > 1]
    return " ".join(tokens[:6]) if tokens else "Unknown Merchant"


def _strip_noise(text: str) -> str:
    cleaned = DATE_RE.sub(" ", text)
    cleaned = TIME_RE.sub(" ", cleaned)
    cleaned = AMOUNT_RE.sub(" ", cleaned)
    cleaned = re.sub(
        r"\b(inward|outward|transfer|payment|withdrawal|stamp|duty|balance|money|in|out)\b",
        " ",
        cleaned,
        flags=re.IGNORECASE,
    )
    cleaned = re.sub(r"\s+", " ", cleaned)
    return cleaned.strip()


def _detect_category(text: str) -> str:
    candidates = [
        "outward transfer",
        "inward transfer",
        "food and drink",
        "withdrawal",
        "payment",
        "transfer",
        "fees",
        "stamp duty",
    ]
    lower = text.lower()
    for candidate in candidates:
        if candidate in lower:
            return candidate.title()
    return ""


def _ocr_pdf_to_text(content: bytes) -> str:
    try:
        from pdf2image import convert_from_bytes
        import pytesseract
        from PIL import Image
    except ImportError as exc:  # pragma: no cover - dependency optional at runtime
        raise ValueError(
            "OCR requires pdf2image + pytesseract. Install them or upload a CSV/JSON export instead."
        ) from exc

    def find_poppler_path() -> Optional[str]:
        env_path = os.environ.get("POPPLER_PATH") or os.environ.get("POPPLER_BIN")
        if env_path and Path(env_path).exists():
            return str(Path(env_path))
        choco_bin = Path(r"C:\ProgramData\chocolatey\bin\pdftoppm.exe")
        if choco_bin.exists():
            return str(choco_bin.parent)
        base = Path(r"C:\ProgramData\chocolatey\lib\poppler\tools")
        if base.exists():
            for candidate in base.glob("poppler-*/Library/bin"):
                if (candidate / "pdftoppm.exe").exists():
                    return str(candidate)
        return None

    def find_tesseract_cmd() -> Optional[str]:
        env_cmd = os.environ.get("TESSERACT_CMD") or os.environ.get("TESSERACT_PATH")
        if env_cmd and Path(env_cmd).exists():
            return str(Path(env_cmd))
        candidates = [
            Path(r"C:\Program Files\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe"),
            Path(r"C:\ProgramData\chocolatey\bin\tesseract.exe"),
        ]
        for candidate in candidates:
            if candidate.exists():
                return str(candidate)
        return None

    poppler_path = find_poppler_path()
    tesseract_cmd = find_tesseract_cmd()
    if tesseract_cmd:
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

    try:
        pages = convert_from_bytes(
            content,
            dpi=200,
            poppler_path=poppler_path,
        ) if poppler_path else convert_from_bytes(content, dpi=200)
        texts = []
        for page in pages:
            texts.append(pytesseract.image_to_string(page))
        return "\n".join(texts)
    except Exception:
        # Fallback to PyMuPDF rendering when Poppler is unavailable.
        try:
            import fitz  # PyMuPDF
        except ImportError as exc:
            raise ValueError(
                "OCR failed. Install Poppler (for pdf2image) or PyMuPDF, and ensure Tesseract is available. "
                "Optionally set POPPLER_PATH or TESSERACT_CMD."
            ) from exc

        try:
            doc = fitz.open(stream=content, filetype="pdf")
            texts = []
            for page in doc:
                pix = page.get_pixmap(dpi=200)
                img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                texts.append(pytesseract.image_to_string(img))
            return "\n".join(texts)
        except Exception as exc:
            raise ValueError(
                "OCR failed using both Poppler and PyMuPDF. Ensure Tesseract is installed and accessible."
            ) from exc


def _parse_ocr_rows(text: str) -> List[Dict[str, str]]:
    if not text:
        return []

    lines = [line.strip() for line in text.splitlines() if line.strip()]
    rows: List[List[str]] = []
    current: List[str] = []

    for line in lines:
        if DATE_RE.search(line):
            if current:
                rows.append(current)
                current = []
        if current or DATE_RE.search(line):
            current.append(line)

    if current:
        rows.append(current)

    parsed_rows: List[Dict[str, Any]] = []
    for row_lines in rows:
        row_text = " ".join(row_lines)
        if _looks_like_header(row_text):
            continue
        date_match = DATE_RE.search(row_text)
        if not date_match:
            continue
        date = _parse_date(date_match.group(0))
        if not date:
            continue
        time_match = TIME_RE.search(row_text)
        time_value = time_match.group(0) if time_match else ""

        direction = ""
        lower = row_text.lower()
        if "outward" in lower or "debit" in lower or "money out" in lower:
            direction = "out"
        if "inward" in lower or "credit" in lower or "money in" in lower:
            direction = "in" if direction == "" else direction

        amount_text = DATE_RE.sub(" ", row_text)
        amount_text = TIME_RE.sub(" ", amount_text)
        amounts = []
        for match in AMOUNT_RE.finditer(amount_text):
            value = match.group(0).strip()
            digits_only = re.sub(r"[^0-9]", "", value)
            if len(digits_only) >= 7 and "," not in value and "." not in value:
                continue
            amounts.append(value)
        if not amounts:
            continue
        primary_amount = amounts[0]
        balance_amount = amounts[-1] if len(amounts) > 1 else ""

        money_in = ""
        money_out = ""
        if direction == "in":
            money_in = primary_amount
        else:
            money_out = primary_amount

        party = _extract_party(row_text)
        category = _detect_category(row_text)
        description = _strip_noise(row_text)
        if party and party != "Unknown Merchant":
            description = description.replace(party, "").strip()

        confidence = 0.0
        if date:
            confidence += 0.35
        if primary_amount:
            confidence += 0.35
        if party and party != "Unknown Merchant":
            confidence += 0.2
        if direction:
            confidence += 0.1

        parsed_rows.append(
            {
                "date_time": f"{date} {time_value}".strip(),
                "money_in": money_in,
                "money_out": money_out,
                "category": category,
                "party": party,
                "description": description,
                "balance": balance_amount,
                "confidence": round(confidence, 2),
            }
        )

    return parsed_rows


def _parse_transactions_from_ocr(text: str) -> List[Dict[str, Any]]:
    rows = _parse_ocr_rows(text)
    if not rows:
        return []
    mapping = {
        "date": "date_time",
        "money_in": "money_in",
        "money_out": "money_out",
        "merchant_name": "party",
        "description": "description",
        "category": "category",
    }
    return normalize_rows_with_mapping(rows, mapping)


def _extract_text_from_pdf(content: bytes) -> str:
    try:
        reader = PdfReader(io.BytesIO(content))
        texts = [page.extract_text() or "" for page in reader.pages]
        return "\n".join(texts)
    except Exception:
        try:
            import fitz  # PyMuPDF
        except Exception:
            return ""
        try:
            doc = fitz.open(stream=content, filetype="pdf")
            return "\n".join(page.get_text() for page in doc)
        except Exception:
            return ""


def _row_quality(rows: List[Dict[str, Any]]) -> float:
    if not rows:
        return 0.0
    valid = 0
    for row in rows:
        if not isinstance(row, dict):
            continue
        date_time = (row.get("date_time") or "").strip()
        amount = (row.get("money_in") or row.get("money_out") or "").strip()
        if date_time and amount:
            valid += 1
    return valid / max(len(rows), 1)


def extract_pdf_rows(content: bytes) -> Dict[str, Any]:
    camelot_available = True
    try:
        import camelot
    except ImportError:
        camelot_available = False

    rows: List[Dict[str, str]] = []
    tmp_path = None
    source = "ocr"
    notes: List[str] = []

    try:
        if camelot_available:
            try:
                with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                    tmp.write(content)
                    tmp_path = tmp.name

                tables = camelot.read_pdf(tmp_path, pages="all", flavor="stream")
                if tables.n:
                    source = "camelot"
                    header: Optional[Dict[str, int]] = None
                    for table in tables:
                        df = table.df
                        for _, row in df.iterrows():
                            row_list = [str(cell) for cell in row.tolist()]
                            row_text = " ".join(row_list)
                            if _looks_like_header(row_text):
                                header = _header_map(row_list) or header
                                continue
                            if header is None:
                                header = _header_map(row_list)
                                if header:
                                    continue

                            if not header:
                                continue

                            rows.append(
                                {
                                    "date_time": row_list[header.get("datetime", -1)] if "datetime" in header else "",
                                    "money_in": row_list[header.get("money_in", -1)] if "money_in" in header else "",
                                    "money_out": row_list[header.get("money_out", -1)] if "money_out" in header else "",
                                    "category": row_list[header.get("category", -1)] if "category" in header else "",
                                    "party": row_list[header.get("party", -1)] if "party" in header else "",
                                    "description": row_list[header.get("description", -1)] if "description" in header else "",
                                    "balance": row_list[header.get("balance", -1)] if "balance" in header else "",
                                    "confidence": 1.0,
                                }
                            )
                    if _row_quality(rows) < 0.4:
                        rows = []
                        source = "ocr"
                        notes.append("camelot_low_quality_fallback")
            except Exception as exc:
                rows = []
                notes.append(f"camelot_error:{type(exc).__name__}")

        if not rows:
            text = _extract_text_from_pdf(content)
            text_rows = _parse_ocr_rows(text)
            if text_rows:
                rows = text_rows
                source = "text"
                notes.append("used_pdf_text")
            else:
                ocr_text = _ocr_pdf_to_text(content)
                rows = _parse_ocr_rows(ocr_text)
                source = "ocr"
                notes.append("used_ocr")
    finally:
        try:
            if tmp_path:
                Path(tmp_path).unlink(missing_ok=True)
        except Exception:
            pass

    columns = ["date_time", "money_in", "money_out", "category", "party", "description", "balance"]
    return {"columns": columns, "rows": rows, "source": source, "notes": notes}


def suggest_mapping(columns: List[str]) -> Dict[str, str]:
    mapping: Dict[str, str] = {}
    for column in columns:
        name = column.lower().strip()
        if "date" in name and "time" in name:
            mapping.setdefault("date", column)
        elif name in {"date", "transaction_date", "posted_date", "post_date"} or "date" in name:
            mapping.setdefault("date", column)
        elif "time" in name:
            mapping.setdefault("time", column)
        elif "money out" in name or "debit" in name or "outflow" in name:
            mapping.setdefault("money_out", column)
        elif "money in" in name or "credit" in name or "inflow" in name:
            mapping.setdefault("money_in", column)
        elif "amount" in name or "value" in name:
            mapping.setdefault("amount", column)
        elif "merchant" in name or "payee" in name or "to" in name and "from" in name:
            mapping.setdefault("merchant_name", column)
        elif "description" in name or "memo" in name or "details" in name or "note" in name:
            mapping.setdefault("description", column)
        elif "category" in name or "type" in name:
            mapping.setdefault("category", column)
    return mapping


def get_preview_schema() -> Dict[str, Any]:
    return {
        "target_fields": [
            {
                "name": "date",
                "required": True,
                "description": "Transaction date (YYYY-MM-DD or similar).",
            },
            {
                "name": "time",
                "required": False,
                "description": "Transaction time if available (HH:MM or HH:MM:SS).",
            },
            {
                "name": "date_time",
                "required": False,
                "description": "Combined date/time string if provided as one column.",
            },
            {
                "name": "amount",
                "required": False,
                "description": "Signed amount. If absent, use money_in/money_out.",
            },
            {
                "name": "money_in",
                "required": False,
                "description": "Credit amount column.",
            },
            {
                "name": "money_out",
                "required": False,
                "description": "Debit amount column.",
            },
            {
                "name": "merchant_name",
                "required": True,
                "description": "Merchant, payee, or counterparty.",
            },
            {
                "name": "description",
                "required": False,
                "description": "Transaction description or memo.",
            },
            {
                "name": "category",
                "required": False,
                "description": "Category/type if provided by the bank.",
            },
            {
                "name": "notes",
                "required": False,
                "description": "Free-form notes field.",
            },
            {
                "name": "balance",
                "required": False,
                "description": "Running balance after the transaction.",
            },
            {
                "name": "confidence",
                "required": False,
                "description": "Parser confidence score (0.0–1.0) for OCR rows.",
            },
        ],
        "mapping_rules": {
            "amount_logic": "If amount is mapped, it is used directly. Otherwise money_out -> positive, money_in -> negative.",
            "date_logic": "If date_time is mapped, it can be used as date; otherwise map date (+ optional time).",
        },
    }


def normalize_rows_with_mapping(rows: List[Dict[str, Any]], mapping: Dict[str, str]) -> List[Dict[str, Any]]:
    transactions: List[Dict[str, Any]] = []
    mapping_lower = {k: v.lower() for k, v in mapping.items() if v}

    for row in rows:
        row_lower = {str(k).lower(): v for k, v in row.items()}

        def value_of(field: str) -> str:
            key = mapping_lower.get(field)
            if not key:
                return ""
            return str(row_lower.get(key, "")).strip()

        def raw_value(field: str) -> Any:
            key = mapping_lower.get(field)
            if not key:
                return ""
            return row_lower.get(key, "")

        date_raw = value_of("date") or value_of("date_time")
        time_raw = value_of("time")
        date_text = f"{date_raw} {time_raw}".strip() if date_raw or time_raw else ""
        date = _parse_statement_date(date_text)

        amount_raw = value_of("amount")
        money_out = value_of("money_out")
        money_in = value_of("money_in")
        amount = 0.0
        if amount_raw:
            amount = _parse_amount(amount_raw)
        elif money_out:
            amount = abs(_parse_amount(money_out))
        elif money_in:
            amount = -abs(_parse_amount(money_in))

        merchant = value_of("merchant_name") or value_of("party") or value_of("payee")
        description = value_of("description")
        notes = value_of("notes") or description
        category_raw = raw_value("category")
        category = _normalize_category(category_raw)

        transactions.append(
            {
                "transaction_id": f"tx_{uuid.uuid4().hex[:10]}",
                "date": date,
                "merchant_name": merchant or "Unknown Merchant",
                "amount": amount,
                "category": category,
                "notes": notes,
            }
        )

    return normalize_transactions(transactions)


def extract_rows_from_upload(filename: str, content: bytes) -> Dict[str, Any]:
    suffix = Path(filename or "").suffix.lower()
    text = _decode_text(content)

    if content[:5] == b"%PDF-" or suffix == ".pdf":
        result = extract_pdf_rows(content)
        suggested = {
            "date": "date_time",
            "money_in": "money_in",
            "money_out": "money_out",
            "merchant_name": "party",
            "description": "description",
            "category": "category",
        }
        result["suggested_mapping"] = suggested
        result["schema"] = get_preview_schema()
        rows = result.get("rows") or []
        confidences = [
            float(r.get("confidence", 0.0))
            for r in rows
            if isinstance(r, dict) and r.get("confidence") is not None
        ]
        if confidences:
            result["confidence_stats"] = {
                "avg": round(sum(confidences) / len(confidences), 3),
                "min": round(min(confidences), 3),
                "max": round(max(confidences), 3),
                "count": len(confidences),
            }
        else:
            result["confidence_stats"] = {"avg": 0.0, "min": 0.0, "max": 0.0, "count": 0}
        return result

    if suffix == ".json" or text.strip().startswith(("{", "[")):
        data = json.loads(text or "[]")
        if isinstance(data, dict):
            data = data.get("transactions") or data.get("data") or []
        if not isinstance(data, list):
            raise ValueError("JSON must be a list of transactions or {\"transactions\": [...]} format.")
        columns = list(data[0].keys()) if data else []
        return {
            "columns": columns,
            "rows": data,
            "source": "json",
            "suggested_mapping": suggest_mapping(columns),
            "schema": get_preview_schema(),
            "confidence_stats": {"avg": 1.0, "min": 1.0, "max": 1.0, "count": len(data)},
        }

    if suffix == ".csv":
        reader = csv.DictReader(io.StringIO(text))
        rows = list(reader)
        columns = reader.fieldnames or []
        return {
            "columns": columns,
            "rows": rows,
            "source": "csv",
            "suggested_mapping": suggest_mapping(columns),
            "schema": get_preview_schema(),
            "confidence_stats": {"avg": 1.0, "min": 1.0, "max": 1.0, "count": len(rows)},
        }

    raise ValueError("Unsupported file type. Please upload a .csv, .json, or .pdf file.")

def parse_transactions_from_pdf(content: bytes) -> List[Dict[str, Any]]:
    result = extract_pdf_rows(content)
    rows = result.get("rows") or []
    if not rows:
        raise ValueError("PDF parsing failed. No rows were extracted.")

    mapping = {
        "date": "date_time",
        "money_in": "money_in",
        "money_out": "money_out",
        "merchant_name": "party",
        "description": "description",
        "category": "category",
    }
    return normalize_rows_with_mapping(rows, mapping)


def parse_transactions_from_upload(filename: str, content: bytes) -> List[Dict[str, Any]]:
    suffix = Path(filename or "").suffix.lower()
    text = _decode_text(content)

    if content[:5] == b"%PDF-":
        return parse_transactions_from_pdf(content)

    if suffix == ".json" or text.strip().startswith(("{", "[")):
        data = json.loads(text or "[]")
        if isinstance(data, dict):
            data = data.get("transactions") or data.get("data") or []
        if not isinstance(data, list):
            raise ValueError("JSON must be a list of transactions or {\"transactions\": [...]} format.")
        return normalize_transactions(data)

    if suffix == ".csv":
        reader = csv.DictReader(io.StringIO(text))
        return normalize_transactions(list(reader))

    if suffix == ".pdf":
        return parse_transactions_from_pdf(content)

    raise ValueError("Unsupported file type. Please upload a .csv, .json, or .pdf file.")


def save_transactions(transactions: List[Dict[str, Any]], source: str = "upload") -> None:
    payload = {
        "source": source,
        "updated_at": datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ"),
        "transactions": transactions,
    }
    STORE_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_transactions() -> Optional[List[Dict[str, Any]]]:
    if not STORE_PATH.exists():
        return None
    data = json.loads(STORE_PATH.read_text(encoding="utf-8") or "{}")
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        tx = data.get("transactions")
        return tx if isinstance(tx, list) else None
    return None
