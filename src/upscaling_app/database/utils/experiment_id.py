import uuid


def make_experiment_id(
    oil_id: int,
    sheet_name: str,
    tag: str,
) -> str:
    key = f"{oil_id}|{sheet_name}|{tag}"

    return str(
        uuid.uuid5(
            uuid.NAMESPACE_DNS,
            key,
        )
    )
