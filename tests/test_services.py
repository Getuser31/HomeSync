"""Unit tests for app services."""
import pytest
from datetime import datetime

from app.services.email_validator import check_email_format
from app.services.period_key_service import generate_period_key


class TestEmailValidator:
    """Tests for the email_validator service."""

    def test_valid_emails(self):
        assert check_email_format("user@example.com") is True
        assert check_email_format("test.user+tag@domain.co.uk") is True
        assert check_email_format("a@b.cd") is True
        assert check_email_format("name_surname@company.org") is True

    def test_invalid_emails(self):
        assert check_email_format("") is False
        assert check_email_format("not-an-email") is False
        assert check_email_format("@domain.com") is False
        assert check_email_format("user@") is False
        assert check_email_format("user@.com") is False
        assert check_email_format("user@domain") is False


class TestPeriodKeyService:
    """Tests for the period_key service."""

    def test_daily_period_key(self):
        dt = datetime(2026, 4, 25, 12, 0, 0)
        key = generate_period_key("Daily", dt)
        assert key == "2026-04-25"

    def test_weekly_period_key(self):
        dt = datetime(2026, 4, 25, 12, 0, 0)
        key = generate_period_key("Weekly", dt)
        assert key == "2026-W17"

    def test_monthly_period_key(self):
        dt = datetime(2026, 4, 25, 12, 0, 0)
        key = generate_period_key("Monthly", dt)
        assert key == "2026-04"

    def test_yearly_period_key_default(self):
        dt = datetime(2026, 4, 25, 12, 0, 0)
        key = generate_period_key("Yearly", dt)
        assert key == "2026"

    def test_default_data_ref_is_now(self):
        """When no data_ref is provided, it should use current time without error."""
        key = generate_period_key("Daily")
        assert key == datetime.now().strftime("%Y-%m-%d")

    def test_edge_case_monthly_january(self):
        dt = datetime(2026, 1, 1)
        key = generate_period_key("Monthly", dt)
        assert key == "2026-01"

    def test_edge_case_weekly_first_week(self):
        dt = datetime(2026, 1, 1)
        key = generate_period_key("Weekly", dt)
        assert key == "2026-W01"
