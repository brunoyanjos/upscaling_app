from dataclasses import dataclass


@dataclass(frozen=True)
class SSDIModelResult:
    model_version: str
    experiment_count: int

    a_initial: float
    b_initial: float

    a_optimized: float
    b_optimized: float
    loss: float


@dataclass(frozen=True)
class BaselineResult:
    model: SSDIModelResult

    a_reference: float
    b_reference: float
    loss_reference: float
