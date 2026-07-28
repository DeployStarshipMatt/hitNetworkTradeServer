"""
Fail-closed authentication tests for the trading server.

POST /api/v1/trade places real orders on BloFin and the server binds 0.0.0.0,
so an unset API_KEY must authenticate nothing and must stop the service from
starting at all.
"""
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

import server


@pytest.fixture
def unconfigured(monkeypatch):
    """Server running with no API_KEY in the environment."""
    monkeypatch.setattr(server, 'API_KEY', None)


@pytest.fixture
def configured(monkeypatch):
    """Server running with a shared secret configured."""
    monkeypatch.setattr(server, 'API_KEY', 'test-shared-secret')


def test_missing_api_key_config_rejects_anonymous_request(unconfigured):
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key(None)
    assert exc.value.status_code == 503


def test_missing_api_key_config_rejects_arbitrary_credentials(unconfigured):
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key('anything-at-all')
    assert exc.value.status_code == 503


def test_missing_api_key_config_rejects_empty_credentials(unconfigured):
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key('')
    assert exc.value.status_code == 503


def test_configured_key_rejects_wrong_key(configured):
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key('wrong-key')
    assert exc.value.status_code == 401


def test_configured_key_rejects_absent_header(configured):
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key(None)
    assert exc.value.status_code == 401


def test_configured_key_accepts_correct_key(configured):
    assert server.verify_api_key('test-shared-secret') is True


def test_configured_key_rejects_prefix_of_correct_key(configured):
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key('test-shared-secre')
    assert exc.value.status_code == 401


def test_configured_key_rejects_non_ascii_header(configured):
    """A junk header must be a clean 401, never a 500 from the comparison."""
    with pytest.raises(HTTPException) as exc:
        server.verify_api_key('tëst-shared-secret')
    assert exc.value.status_code == 401


def test_trade_endpoint_refuses_orders_when_api_key_unset(unconfigured):
    """The order-placement route must not authenticate an unconfigured server."""
    client = TestClient(server.app)
    response = client.post('/api/v1/trade', json={'symbol': 'BTC-USDT', 'side': 'buy'})
    assert response.status_code == 503


def test_trade_endpoint_rejects_wrong_key(configured):
    client = TestClient(server.app)
    response = client.post(
        '/api/v1/trade',
        json={'symbol': 'BTC-USDT', 'side': 'buy'},
        headers={'X-API-Key': 'wrong-key'},
    )
    assert response.status_code == 401


def test_startup_guard_raises_when_api_key_unset(unconfigured):
    with pytest.raises(RuntimeError):
        server.require_api_key_configured()


def test_startup_guard_passes_when_api_key_set(configured):
    server.require_api_key_configured()


def test_application_refuses_to_start_without_api_key(unconfigured):
    """Running the ASGI lifespan must abort before any worker thread starts."""
    with pytest.raises(RuntimeError):
        with TestClient(server.app):
            pass
