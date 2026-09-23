from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SSMDRegimeResult:
    nozzle_diameter: float
    has_gas: bool

    eta: float
    c_coef: float
    d_coef: float


@dataclass(frozen=True)
class SSMDModelResult:
    model_version: str
    experiment_count: int
    regimes: tuple[SSMDRegimeResult, ...]
    loss: float


@dataclass(frozen=True)
class BaselineResult:
    model: SSMDModelResult
    global_model: SSMDModelResult
    reference: SSMDModelResult
