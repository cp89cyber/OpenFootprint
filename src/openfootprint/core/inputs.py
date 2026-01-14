from __future__ import annotations

from dataclasses import dataclass

import phonenumbers


def normalize_email(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def normalize_username(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value.lower() if value else None


def normalize_name(value: str | None) -> str | None:
    if value is None:
        return None
    value = " ".join(value.strip().split())
    return value if value else None


def normalize_phone(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    if not value:
        return None
    parsed = phonenumbers.parse(value, None)
    if not phonenumbers.is_valid_number(parsed):
        raise ValueError("Phone number is not valid E.164")
    return phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)


@dataclass(frozen=True)
class LookupInputs:
    username: str | None
    email: str | None
    phone: str | None
    name: str | None

    @classmethod
    def from_raw(
        cls,
        username: str | None,
        email: str | None,
        phone: str | None,
        name: str | None,
    ) -> "LookupInputs":
        return cls(
            username=normalize_username(username),
            email=normalize_email(email),
            phone=normalize_phone(phone),
            name=normalize_name(name),
        )
