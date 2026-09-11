#!/usr/bin/env python3
"""Local unit tests for Silver pure-Python helpers (no PySpark required)."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from silver_common import (  # noqa: E402
    calculate_pass_percentage,
    calculate_summary_metrics,
    entity_dq_categories,
    is_blank,
    is_numeric_identifier,
    is_valid_customer_segment,
    is_valid_email_format,
    is_valid_iso_date_string,
    parse_decimal_string,
    parse_int_string,
)


def test_is_blank() -> None:
    assert is_blank("") is True
    assert is_blank("   ") is True
    assert is_blank(None) is True
    assert is_blank("x") is False


def test_numeric_identifier() -> None:
    assert is_numeric_identifier("12345") is True
    assert is_numeric_identifier("INVALID") is False
    assert is_numeric_identifier("") is False


def test_email() -> None:
    assert is_valid_email_format("a@b.com") is True
    assert is_valid_email_format("invalid-email-format") is False


def test_iso_date() -> None:
    assert is_valid_iso_date_string("2024-01-15") is True
    assert is_valid_iso_date_string("NOT-A-DATE") is False
    assert is_valid_iso_date_string("31/13/2024") is False


def test_parse_decimal() -> None:
    assert parse_decimal_string("19.99") == 19.99
    assert parse_decimal_string("INVALID") is None


def test_parse_int() -> None:
    assert parse_int_string("3") == 3
    assert parse_int_string("-1") == -1
    assert parse_int_string("abc") is None


def test_customer_segment() -> None:
    assert is_valid_customer_segment("Premium") is True
    assert is_valid_customer_segment("Standard") is True
    assert is_valid_customer_segment("Basic") is True
    assert is_valid_customer_segment("Gold") is False
    assert is_valid_customer_segment("") is False


def test_pass_percentage() -> None:
    assert calculate_pass_percentage(100, 95) == 95.0
    assert calculate_pass_percentage(0, 0) is None
    assert calculate_pass_percentage(9, 0) == 0.0


def test_summary_metrics() -> None:
    metrics = calculate_summary_metrics(1006, 60)
    assert metrics["rows_tested"] == 1006
    assert metrics["rows_failed"] == 60
    assert metrics["rows_passed"] == 946
    assert metrics["pass_percentage"] == 946 / 1006 * 100.0

    zero_tested = calculate_summary_metrics(0, 0)
    assert zero_tested["rows_passed"] == 0
    assert zero_tested["pass_percentage"] is None


def test_entity_dq_categories() -> None:
    assert entity_dq_categories("customers") == (
        "completeness",
        "uniqueness",
        "type_validation",
        "business_logic",
    )
    assert entity_dq_categories("orders") == (
        "completeness",
        "uniqueness",
        "type_validation",
        "referential_integrity",
        "business_logic",
    )


def main() -> None:
    test_is_blank()
    test_numeric_identifier()
    test_email()
    test_iso_date()
    test_parse_decimal()
    test_parse_int()
    test_customer_segment()
    test_pass_percentage()
    test_summary_metrics()
    test_entity_dq_categories()
    print("All Silver helper tests passed.")


if __name__ == "__main__":
    main()
