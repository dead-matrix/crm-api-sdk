"""Tests for PaymentsAPI."""
from __future__ import annotations

import pytest
import httpx

from conftest import success_response
from crm_api.models import PaymentsCalculateInput, InvoiceDraftInput, InvoiceIssueInput, RefundInput


class TestPaymentsAPI:
    @pytest.mark.asyncio
    async def test_calculate_payment_success(self, client_factory):
        """Test calculate_payment returns PaymentsCalculateResult."""
        mock_data = {
            "amount_minor": 198000,
            "amount_usd": 20.0,
            "currency": "RUB",
            "items": [
                {
                    "id": 1,
                    "title": "Масслукинг",
                    "unit_price_minor": 99000,
                    "discount_percent": 0,
                    "unit_price_discounted_minor": 99000,
                    "quantity": 2,
                    "line_total_minor": 198000,
                }
            ]
        }
        routes = {
            "POST /api/payments/calculate": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            inp = PaymentsCalculateInput(product_ids=[1], discount_percent=0, months=2)
            result = await client.calculate_payment(inp)
            
            assert result.amount_minor == 198000
            assert result.amount_usd == 20.0
            assert result.currency == "RUB"
            assert len(result.items) == 1
            assert result.items[0].id == 1
            assert result.items[0].title == "Масслукинг"
            assert result.items[0].line_total_minor == 198000

    @pytest.mark.asyncio
    async def test_create_invoice_draft_success(self, client_factory):
        """Test create_invoice_draft returns InvoiceDraftResult."""
        mock_data = {
            "uuid": "inv-12345678-abcd-1234-efgh",
            "pay_link": "https://pay.example.com/inv-12345678",
            "status": "draft",
        }
        routes = {
            "POST /api/payments/invoice/draft": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            inp = InvoiceDraftInput(
                client_id=123, product_ids=[1, 2], discount_percent=10, months=1, provider="yookassa"
            )
            result = await client.create_invoice_draft(inp)
            
            assert result.uuid == "inv-12345678-abcd-1234-efgh"
            assert result.pay_link == "https://pay.example.com/inv-12345678"
            assert result.status == "draft"

    @pytest.mark.asyncio
    async def test_issue_invoice_success(self, client_factory):
        """Test issue_invoice returns InvoiceIssueResult."""
        mock_data = {
            "pay_url": "https://yookassa.ru/pay/abc123",
            "status": "pending",
        }
        routes = {
            "POST /api/payments/invoice/issue": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            inp = InvoiceIssueInput(uuid="inv-12345678-abcd-1234-efgh", client_email="test@example.com")
            result = await client.issue_invoice(inp)
            
            assert result.pay_url == "https://yookassa.ru/pay/abc123"
            assert result.status == "pending"

    @pytest.mark.asyncio
    async def test_get_payments_success(self, client_factory):
        """Test get_payments returns list of PaymentHistoryItem."""
        mock_data = [
            {
                "uuid": "pay-001",
                "date_create": "2024-01-10T10:00:00Z",
                "date_invoiced": "2024-01-10T10:05:00Z",
                "date_paid": "2024-01-10T10:10:00Z",
                "status": "paid",
                "amount_minor": 99000,
                "discount_percent": 0,
                "currency": "RUB",
                "items": [{"id": 1, "title": "Product"}],
                "client_email": "user@example.com",
                "pay_url": None,
                "provider": "yookassa",
                "activation": [
                    {"bot_id": 1, "code": "ABC123", "is_used": False, "url": "https://t.me/bot?start=ABC123"}
                ],
            }
        ]
        routes = {
            "GET /api/payments/{user_id}": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.get_payments(user_id=123)
            
            assert len(result) == 1
            p = result[0]
            assert p.uuid == "pay-001"
            assert p.status == "paid"
            assert p.amount_minor == 99000
            assert len(p.activation) == 1
            assert p.activation[0].code == "ABC123"
            assert p.activation[0].is_used is False

    @pytest.mark.asyncio
    async def test_confirm_payment_success(self, client_factory):
        """Test confirm_payment returns ConfirmPaymentResult."""
        mock_data = {"uuid": "pay-001", "status": "confirmed"}
        routes = {
            "GET /api/payments/confirm/{uuid}": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.confirm_payment(uuid="pay-001")
            assert result.uuid == "pay-001"
            assert result.status == "confirmed"

    @pytest.mark.asyncio
    async def test_refund_payment_success(self, client_factory):
        """Test refund_payment returns RefundResult."""
        mock_data = {
            "uuid": "pay-001",
            "provider": "yookassa",
            "allowed": True,
            "message": "Refund processed",
            "status": "refunded",
        }
        routes = {
            "POST /api/payments/refund/{uuid}": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.refund_payment(uuid="pay-001", payload=RefundInput(reason="Customer request"))
            assert result.uuid == "pay-001"
            assert result.allowed is True
            assert result.message == "Refund processed"

    @pytest.mark.asyncio
    async def test_refund_payment_without_payload(self, client_factory):
        """Test refund_payment without payload."""
        mock_data = {
            "uuid": "pay-002",
            "provider": "cryptocloud",
            "allowed": False,
            "message": "Refund not allowed",
        }
        routes = {
            "POST /api/payments/refund/{uuid}": lambda req: success_response(mock_data),
        }
        async with client_factory(routes) as client:
            result = await client.refund_payment(uuid="pay-002")
            assert result.uuid == "pay-002"
            assert result.allowed is False

