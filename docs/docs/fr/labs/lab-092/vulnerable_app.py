def validate(value: str) -> str:
    if not value.strip():
        raise ValueError("value is required")
    return value.strip()
