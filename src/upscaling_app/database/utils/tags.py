def dispersion_kind(tag: str) -> str:
    if "Untreated" in tag:
        return "Untreated"
    if "SSDI" in tag:
        return "SSDI"
    return "SSMD"


def normalize_distribution_tag(
    column: str,
    oil_id: int,
) -> tuple[str, bool]:
    has_gas = column.endswith("-gas")
    tag = column.removesuffix("-gas")

    if tag == "Untreated":
        return f"{oil_id}-Untreated", has_gas

    if tag in {"C9500", "IBC"}:
        return f"SSDI-{tag}", has_gas

    if tag.startswith("WJ"):
        return f"WJ-{tag.removeprefix('WJ')}", has_gas

    raise ValueError(f"Unknown distribution tag: {column}")


def water_jet_fraction(tag: str) -> float:
    if not tag.startswith("WJ-"):
        return 0.0

    percentage = tag.removeprefix("WJ-").removesuffix("%")

    return float(percentage) / 100.0
