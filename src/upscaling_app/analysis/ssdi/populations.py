SSDI_ALL_OILS = (
    3014,
    3015,
    3016,
    4661,
    4662,
    4663,
    4664,
    4665,
    4666,
    4667,
)


SSDI_RESIDUAL_SENSITIVITY_OILS = (
    3016,
    4665,
)


SSDI_EXTENDED_SENSITIVITY_OILS = (
    3016,
    4662,
    4665,
)


SSDI_RETAINED_OILS = tuple(
    oil_id for oil_id in SSDI_ALL_OILS if oil_id not in SSDI_EXTENDED_SENSITIVITY_OILS
)
