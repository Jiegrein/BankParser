"""
Base helpers for LLM services: shared prompt and robust JSON parsing.
"""

from __future__ import annotations

from typing import Dict, Any, Optional, List
import json
import re
import hashlib

from .interface import LLMServiceInterface
from app.models import BankStatement, Transaction
from abc import abstractmethod


class BaseLLMService(LLMServiceInterface):
    """Base class providing common helpers for LLM services.

    Concrete subclasses must implement parse_text_statement and parse_image_statement.
    """

    # ---------- Prompt ----------
    def _get_parsing_prompt(self) -> str:
        """Standard parsing prompt used across providers for consistent outputs."""
        return (
            """
        You are a bank statement parsing expert. Extract and standardize the following bank statement data into the specified JSON format.

        Required fields:
        - account_holder: Full name of the account holder
        - bank_name: Name of the bank
        - account_number: Account number (keep last 4 digits visible, mask others with *)
        - statement_period: Object with start_date and end_date (YYYY-MM-DD format)
        - opening_balance: Starting balance as a number
        - closing_balance: Ending balance as a number
        - transactions: Array of transaction objects
        - currency: Currency code (default USD)

        For each transaction, include:
        - date: Transaction date (YYYY-MM-DD format)
        - description: Transaction description
        - amount: Transaction amount (positive number)
        - type: "credit" or "debit"
        - category: Transaction category (optional)
        - balance: Running balance after transaction (optional)

        Return ONLY valid JSON (no markdown code fences, no comments, no explanations), do not use "\n" in the JSON.
        Do not include trailing commas. Use numbers, not strings, for amounts/balances.
        If there is a page that is sent and does not look like a statement, example(detail pages, contact information pages, etc.) from the bank, do not send false data, just send transactions as [].
        Schema:
        {
            "account_holder": string,
            "bank_name": string,
            "account_number": string,  // last 4 visible, others masked with *
            "statement_period": { "start_date": "YYYY-MM-DD", "end_date": "YYYY-MM-DD" },
            "opening_balance": number,
            "closing_balance": number,
            "transactions": [
                { "date": "YYYY-MM-DD", "description": string, "amount": number, "type": "credit"|"debit", "category": string? }
            ],
            "currency": "USD",
            "has_more": boolean,
            "next_page_hint": string?
        }
        Output the JSON object only.
        """
        ).strip()

    # ---------- JSON Mode Heuristic ----------
    def _is_json_mode_supported(self, model_name: str) -> bool:
        """Return True if the model likely supports response_format json_object."""
        normalized = model_name.lower()
        return any(key in normalized for key in ["gpt-4o", "gpt-4.1", "gpt-4.1-mini"])  # expandable

    # ---------- JSON Parsing Helpers ----------
    def _strip_code_fences(self, content: str) -> str:
        """Remove markdown code fences like ```json ... ``` or ``` ... ```."""
        content = content.strip()
        if content.startswith("```") and content.endswith("```"):
            content = content[3:-3]
        # Remove optional language tag on first line
        content = re.sub(r"^\s*json\s*\n", "", content, flags=re.IGNORECASE)
        return content.strip()

    def _remove_trailing_commas(self, content: str) -> str:
        """Best-effort removal of trailing commas before } or ]."""
        prev = None
        while prev != content:
            prev = content
            content = re.sub(r",\s*([}\]])", r"\1", content)
        return content

    def _normalize_number_separators(self, content: str) -> str:
        """Remove thousands separators in unquoted numbers like 12,345.67 -> 12345.67.
        This reduces JSON parse errors when models format numbers for readability.
        """
        def repl(match: re.Match) -> str:
            number = match.group(0)
            return number.replace(",", "")

        # Match numbers not inside quotes: use a negative lookbehind/ahead for quotes around the entire token
        # Approximation: replace sequences of digits with internal commas optionally followed by decimal part
        pattern = re.compile(r"(?<![\w\"'])\d{1,3}(?:,\d{3})+(?:\.\d+)?(?![\w\"'])")
        return pattern.sub(repl, content)

    def _extract_json_from_fenced_block(self, content: str) -> Optional[str]:
        """Find a ```json ... ``` or ``` ... ``` fenced block anywhere and return its body."""
        fence_json = re.search(r"```\s*json\s*\n([\s\S]*?)```", content, re.IGNORECASE)
        if fence_json:
            return fence_json.group(1).strip()
        fence = re.search(r"```\s*\n([\s\S]*?)```", content)
        if fence:
            return fence.group(1).strip()
        return None

    def _extract_first_json_object(self, content: str) -> Optional[str]:
        """Extract the first balanced JSON object substring starting at the first '{'."""
        start = content.find("{")
        if start == -1:
            return None
        depth = 0
        in_string = False
        escape = False
        for idx in range(start, len(content)):
            ch = content[idx]
            if in_string:
                if escape:
                    escape = False
                elif ch == "\\":
                    escape = True
                elif ch == '"':
                    in_string = False
                continue
            else:
                if ch == '"':
                    in_string = True
                elif ch == '{':
                    depth += 1
                elif ch == '}':
                    depth -= 1
                    if depth == 0:
                        return content[start:idx + 1]
        return None

    def _parse_response_json(self, raw_content: str) -> Dict[str, Any]:
        """Robustly parse JSON from LLM responses with common cleanup steps."""
        # Try raw
        try:
            return json.loads(raw_content)
        except Exception:
            pass

        # Strip code fences and try again
        cleaned = self._strip_code_fences(raw_content)
        try:
            return json.loads(cleaned)
        except Exception:
            pass

        # Explicit fenced block anywhere in content
        fenced = self._extract_json_from_fenced_block(raw_content)
        if fenced:
            try:
                return json.loads(fenced)
            except Exception:
                # attempt with number normalization and trailing comma cleanup
                fenced_norm = self._normalize_number_separators(self._remove_trailing_commas(fenced))
                return json.loads(fenced_norm)

        # Extract first JSON object and try
        obj = self._extract_first_json_object(cleaned)
        if obj:
            try:
                return json.loads(obj)
            except Exception:
                sanitized = self._remove_trailing_commas(obj)
                try:
                    return json.loads(sanitized)
                except Exception:
                    sanitized_norm = self._normalize_number_separators(sanitized)
                    return json.loads(sanitized_norm)

        # Final attempt: trailing comma cleanup on full cleaned content
        sanitized_full = self._remove_trailing_commas(cleaned)
        try:
            return json.loads(sanitized_full)
        except Exception:
            sanitized_full_norm = self._normalize_number_separators(sanitized_full)
            return json.loads(sanitized_full_norm)

    # ---------- Conversion Helpers ----------
    def _convert_to_bank_statement(self, data: Dict[str, Any]) -> BankStatement:
        """Convert parsed dict to BankStatement model."""
        transactions: List[Transaction] = []
        for txn_data in data.get("transactions", []):
            transaction = Transaction(
                date=txn_data["date"],
                description=txn_data["description"],
                amount=float(txn_data["amount"]),
                type=txn_data["type"],
                category=txn_data.get("category"),
                balance=float(txn_data["balance"]) if txn_data.get("balance") else None,
            )
            transactions.append(transaction)

        bank_statement = BankStatement(
            account_holder=data["account_holder"],
            bank_name=data["bank_name"],
            account_number=data["account_number"],
            statement_period=data["statement_period"],
            opening_balance=float(data["opening_balance"]),
            closing_balance=float(data["closing_balance"]),
            transactions=transactions,
            currency=data.get("currency", "USD"),
        )
        return bank_statement

    # ---------- Pagination Support (Template Method) ----------
    @abstractmethod
    async def _single_text_call(self, text_content: str, next_page_hint: str | None) -> Dict[str, Any]:
        """Perform one text-only LLM call and return parsed JSON as dict."""
        raise NotImplementedError

    @abstractmethod
    async def _single_image_call(self, base64_images: List[str], next_page_hint: str | None) -> Dict[str, Any]:
        """Perform one vision LLM call and return parsed JSON as dict."""
        raise NotImplementedError

    def _merge_chunks(self, first: Dict[str, Any], nxt: Dict[str, Any]) -> Dict[str, Any]:
        """Merge two chunks of parsed statement data."""
        merged = dict(first)
        # Merge transactions with dedupe
        seen = set(
            (t.get("date"), t.get("description"), float(t.get("amount", 0.0)))
            for t in merged.get("transactions", [])
        )
        for t in nxt.get("transactions", []):
            key = (t.get("date"), t.get("description"), float(t.get("amount", 0.0)))
            if key not in seen:
                merged.setdefault("transactions", []).append(t)
                seen.add(key)

        # Prefer most recent closing_balance if provided
        if "closing_balance" in nxt:
            merged["closing_balance"] = nxt["closing_balance"]

        # has_more propagation
        merged["has_more"] = bool(nxt.get("has_more"))
        if nxt.get("next_page_hint"):
            merged["next_page_hint"] = nxt.get("next_page_hint")
        else:
            merged.pop("next_page_hint", None)

        return merged

    async def _paginate_and_collect(
        self,
        first_chunk: Dict[str, Any],
        fetch_next: callable,
        max_followups: int = 3,
    ) -> Dict[str, Any]:
        """Follow continuation hints and merge chunks up to a limit."""
        merged = dict(first_chunk)
        attempts = 0
        while attempts < max_followups and merged.get("has_more") and merged.get("next_page_hint"):
            hint = merged.get("next_page_hint")
            nxt = await fetch_next(hint)
            merged = self._merge_chunks(merged, nxt)
            attempts += 1
        # Cleanup pagination fields from final output
        merged.pop("has_more", None)
        merged.pop("next_page_hint", None)
        return merged

    # ---------- Public Implementations (reusable across providers) ----------
    async def parse_text_statement(self, text_content: str) -> BankStatement:
        first = await self._single_text_call(text_content, next_page_hint=None)

        async def _fetch(hint: str) -> Dict[str, Any]:
            return await self._single_text_call(text_content, next_page_hint=hint)

        merged = await self._paginate_and_collect(first, _fetch)
        return self._convert_to_bank_statement(merged)

    async def parse_image_statement(self, base64_images: List[str]) -> BankStatement:
        """Process unique images page-by-page (no continuation), then merge results."""
        merged: Optional[Dict[str, Any]] = None
        seen_hashes: set[str] = set()
        for idx, img in enumerate(base64_images):
            img_hash = hashlib.sha1(img.encode("utf-8")).hexdigest()
            if img_hash in seen_hashes:
                continue
            seen_hashes.add(img_hash)

            page_hint = f"page={idx + 1}"
            chunk = await self._single_image_call([img], next_page_hint=page_hint)

            if merged is None:
                merged = chunk
            else:
                merged = self._merge_chunks(merged, chunk)

        if merged is None:
            merged = {
                "account_holder": "",
                "bank_name": "",
                "account_number": "",
                "statement_period": {"start_date": "", "end_date": ""},
                "opening_balance": 0.0,
                "closing_balance": 0.0,
                "transactions": [],
                "currency": "USD",
            }

        merged.pop("has_more", None)
        merged.pop("next_page_hint", None)

        return self._convert_to_bank_statement(merged)


