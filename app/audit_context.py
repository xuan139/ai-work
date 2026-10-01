from contextvars import ContextVar, Token
from typing import Any


_AUDIT_CONTEXT: ContextVar[dict[str, Any]] = ContextVar("audit_context", default={})


def set_audit_context(values: dict[str, Any]) -> Token:
    return _AUDIT_CONTEXT.set({key: value for key, value in values.items() if value is not None})


def reset_audit_context(token: Token) -> None:
    _AUDIT_CONTEXT.reset(token)


def audit_context() -> dict[str, Any]:
    return dict(_AUDIT_CONTEXT.get())
