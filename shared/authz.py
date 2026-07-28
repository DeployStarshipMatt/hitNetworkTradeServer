"""
Shared authorization helpers.

Dependency-free on purpose so both services (and their tests) can import it
without pulling in discord.py or FastAPI.
"""
from typing import Iterable, Optional


def is_authorized_signal_poster(
    user_id: int,
    role_names: Iterable[str],
    allowed_user_ids: Iterable[int],
    required_role_name: Optional[str]
) -> bool:
    """
    Decide whether a Discord poster may trigger a live trade.

    Fails closed: with no allowlist and no required role configured, nobody is
    authorized. A signal accepted from the monitored channel places a real
    order on the copy-trading master account, which followers auto-mirror, so
    an unconfigured filter must authorize nothing rather than everything.

    Args:
        user_id: Discord user ID of the poster
        role_names: Role names the poster holds (empty for non-guild users)
        allowed_user_ids: Configured ALLOWED_USER_IDS allowlist
        required_role_name: Configured REQUIRED_ROLE_NAME, if any

    Returns:
        True only if at least one filter is configured and every configured
        filter passes.
    """
    allowed_ids = set(allowed_user_ids or [])
    required_role = (required_role_name or '').strip()

    # No filter configured - authorize nothing.
    if not allowed_ids and not required_role:
        return False

    if allowed_ids and user_id not in allowed_ids:
        return False

    if required_role and required_role not in set(role_names or []):
        return False

    return True
