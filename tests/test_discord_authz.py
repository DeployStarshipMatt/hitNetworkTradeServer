"""
Fail-closed authorization tests for Discord signal posters.

A signal accepted from the monitored channel places a real order on the
copy-trading master account, which followers auto-mirror. With no allowlist
and no required role configured, nobody may be authorized.
"""
import ast
from pathlib import Path

from shared.authz import is_authorized_signal_poster

BOT_SOURCE = Path(__file__).resolve().parent.parent / 'discord-bot' / 'bot.py'


def test_no_filters_configured_authorizes_nobody():
    assert is_authorized_signal_poster(
        user_id=1,
        role_names=['Signals'],
        allowed_user_ids=[],
        required_role_name=None,
    ) is False


def test_blank_role_name_is_not_a_filter():
    assert is_authorized_signal_poster(
        user_id=1,
        role_names=[],
        allowed_user_ids=[],
        required_role_name='   ',
    ) is False


def test_allowlisted_user_is_authorized():
    assert is_authorized_signal_poster(
        user_id=42,
        role_names=[],
        allowed_user_ids=[42, 43],
        required_role_name=None,
    ) is True


def test_non_allowlisted_user_is_rejected():
    assert is_authorized_signal_poster(
        user_id=99,
        role_names=[],
        allowed_user_ids=[42, 43],
        required_role_name=None,
    ) is False


def test_required_role_present_is_authorized():
    assert is_authorized_signal_poster(
        user_id=99,
        role_names=['Member', 'Signals'],
        allowed_user_ids=[],
        required_role_name='Signals',
    ) is True


def test_required_role_absent_is_rejected():
    assert is_authorized_signal_poster(
        user_id=99,
        role_names=['Member'],
        allowed_user_ids=[],
        required_role_name='Signals',
    ) is False


def test_user_with_no_roles_is_rejected_when_role_required():
    """Non-guild users (DMs, webhooks) carry no roles and must not slip through."""
    assert is_authorized_signal_poster(
        user_id=99,
        role_names=[],
        allowed_user_ids=[],
        required_role_name='Signals',
    ) is False


def test_both_filters_must_pass():
    assert is_authorized_signal_poster(
        user_id=42,
        role_names=['Member'],
        allowed_user_ids=[42],
        required_role_name='Signals',
    ) is False
    assert is_authorized_signal_poster(
        user_id=42,
        role_names=['Signals'],
        allowed_user_ids=[42],
        required_role_name='Signals',
    ) is True


def _authorization_method():
    tree = ast.parse(BOT_SOURCE.read_text(encoding='utf-8'))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == '_is_authorized_user':
            return node
    raise AssertionError('_is_authorized_user not found in discord-bot/bot.py')


def test_bot_authorization_has_no_unconditional_allow():
    """
    bot.py cannot be imported here (discord.py is a runtime-only dependency),
    so guard the fail-open regression at the source level instead.
    """
    method = _authorization_method()
    returns = [n for n in ast.walk(method) if isinstance(n, ast.Return)]
    literal_true_returns = [
        n for n in returns
        if isinstance(n.value, ast.Constant) and n.value.value is True
    ]
    assert literal_true_returns == []


def test_bot_authorization_delegates_to_shared_helper():
    method = _authorization_method()
    called = {
        n.func.id for n in ast.walk(method)
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)
    }
    assert 'is_authorized_signal_poster' in called
