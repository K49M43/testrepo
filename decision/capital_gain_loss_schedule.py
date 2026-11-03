"""Source-linked capital-gain/loss netting for explicitly supplied allocations.

This module validates arithmetic and the character restrictions in sections
108, 111 and 121 of the Income-tax Act, 2025. It deliberately does not choose
an allocation priority across tax-rate buckets, establish asset character, or
calculate tax. Those remain explicit inputs / downstream qualification gates.
"""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from typing import Any, Literal


ZERO = Decimal("0")
Character = Literal["short", "long"]
TaxBucket = Literal["section76", "section196", "section197", "section198"]


def _positive(value: Decimal | int | str, field: str, *, allow_zero: bool = False) -> Decimal:
    result = value if isinstance(value, Decimal) else Decimal(str(value))
    if not result.is_finite() or result < ZERO or (not allow_zero and result == ZERO):
        qualifier = "non-negative" if allow_zero else "positive"
        raise ValueError(f"{field} must be finite and {qualifier}")
    return result


def _tax_year_start(value: str) -> int:
    try:
        start, end = value.split("-")
        start_year, end_year = int(start), int(end)
    except (AttributeError, ValueError) as error:
        raise ValueError(f"invalid tax-year label: {value!r}") from error
    if end_year != (start_year + 1) % 100 or len(start) != 4 or len(end) != 2:
        raise ValueError(f"invalid tax-year label: {value!r}")
    return start_year


@dataclass(frozen=True)
class Gain:
    gain_id: str
    source_event_id: str
    lot_id: str
    tax_year: str
    amount_inr: Decimal
    character: Character
    tax_bucket: TaxBucket


@dataclass(frozen=True)
class Loss:
    loss_id: str
    source_event_id: str
    lot_id: str
    origin_tax_year: str
    amount_inr: Decimal
    character: Character
    return_filed_under_263_1: bool
    return_evidence_reference: str = ""


@dataclass(frozen=True)
class Offset:
    loss_id: str
    gain_id: str
    amount_inr: Decimal


@dataclass(frozen=True)
class ScheduleResult:
    tax_year: str
    gross_gains_by_bucket: dict[str, Decimal]
    offsets_by_bucket: dict[str, Decimal]
    candidate_gains_after_explicit_offsets_by_bucket: dict[str, Decimal]
    loss_trace: list[dict[str, Any]]
    offset_trace: list[dict[str, str]]
    unallocated_losses: dict[str, Decimal]
    carryforward_losses: dict[str, Decimal]
    tax_application_allowed: bool = False


def _validate_character(value: str, field: str) -> None:
    if value not in {"short", "long"}:
        raise ValueError(f"{field} character must be 'short' or 'long'")


def build_schedule(
    tax_year: str,
    gains: list[Gain],
    losses: list[Loss],
    offsets: list[Offset],
) -> ScheduleResult:
    """Validate caller-selected offsets and return traceable net gain buckets.

    No allocation is inferred. Every offset must be supplied and must satisfy
    the statutory holding-period compatibility. Carried losses must have a
    timely section 263(1) return and be used within eight succeeding years.
    """
    year = _tax_year_start(tax_year)
    if year < 2026:
        raise NotImplementedError("pre-2026 losses require a separately validated section 536 transition record")
    gain_by_id: dict[str, Gain] = {}
    loss_by_id: dict[str, Loss] = {}
    for item in gains:
        if (not item.gain_id or item.gain_id in gain_by_id
                or not item.source_event_id.strip() or not item.lot_id.strip()):
            raise ValueError("gain IDs, source event IDs, and lot IDs must be present; gain IDs must be unique")
        if item.tax_year != tax_year:
            raise ValueError(f"gain {item.gain_id} must belong to {tax_year}")
        _validate_character(item.character, f"gain {item.gain_id}")
        if item.tax_bucket not in {"section76", "section196", "section197", "section198"}:
            raise ValueError(f"unsupported tax bucket for gain {item.gain_id}")
        expected_character = "long" if item.tax_bucket in {"section197", "section198"} else "short"
        if item.character != expected_character:
            raise ValueError(f"gain {item.gain_id} character conflicts with {item.tax_bucket}")
        gain_by_id[item.gain_id] = Gain(item.gain_id, item.source_event_id, item.lot_id, item.tax_year,
                                        _positive(item.amount_inr, f"gain {item.gain_id} amount"),
                                        item.character, item.tax_bucket)
    for item in losses:
        if (not item.loss_id or item.loss_id in loss_by_id
                or not item.source_event_id.strip() or not item.lot_id.strip()):
            raise ValueError("loss IDs, source event IDs, and lot IDs must be present; loss IDs must be unique")
        if not isinstance(item.return_filed_under_263_1, bool):
            raise ValueError(f"loss {item.loss_id} return-filing status must be explicitly true or false")
        if not isinstance(item.return_evidence_reference, str):
            raise ValueError(f"loss {item.loss_id} return evidence reference must be text")
        if item.return_filed_under_263_1 and not item.return_evidence_reference.strip():
            raise ValueError(f"loss {item.loss_id} requires a section 263(1) return evidence reference")
        _validate_character(item.character, f"loss {item.loss_id}")
        origin = _tax_year_start(item.origin_tax_year)
        if origin < 2026:
            raise NotImplementedError("pre-2026 losses require a separately validated section 536 transition record")
        age = year - origin
        if age < 0:
            raise ValueError(f"loss {item.loss_id} cannot be used before its origin tax year")
        if age > 0 and (age > 8 or not item.return_filed_under_263_1):
            raise ValueError(f"loss {item.loss_id} is not eligible for carry-forward use")
        loss_by_id[item.loss_id] = Loss(item.loss_id, item.source_event_id, item.lot_id, item.origin_tax_year,
                                        _positive(item.amount_inr, f"loss {item.loss_id} amount"),
                                        item.character, item.return_filed_under_263_1,
                                        item.return_evidence_reference)

    used_by_gain: dict[str, Decimal] = {}
    used_by_loss: dict[str, Decimal] = {}
    bucket_offsets: dict[str, Decimal] = {}
    offset_rows: list[dict[str, str]] = []
    for allocation in offsets:
        if allocation.loss_id not in loss_by_id or allocation.gain_id not in gain_by_id:
            raise ValueError("each offset must reference a supplied loss and gain")
        amount = _positive(allocation.amount_inr, "offset amount")
        loss = loss_by_id[allocation.loss_id]
        gain = gain_by_id[allocation.gain_id]
        # Section 108: same-year ST losses can offset any capital asset; LT
        # losses only LT. Section 111 preserves these restrictions on carryover.
        if loss.character == "long" and gain.character != "long":
            raise ValueError(f"long-term loss {loss.loss_id} cannot offset short-term gain {gain.gain_id}")
        new_loss_total = used_by_loss.get(loss.loss_id, ZERO) + amount
        new_gain_total = used_by_gain.get(gain.gain_id, ZERO) + amount
        if new_loss_total > loss.amount_inr:
            raise ValueError(f"offsets exceed loss {loss.loss_id}")
        if new_gain_total > gain.amount_inr:
            raise ValueError(f"offsets exceed gain {gain.gain_id}")
        used_by_loss[loss.loss_id] = new_loss_total
        used_by_gain[gain.gain_id] = new_gain_total
        bucket_offsets[gain.tax_bucket] = bucket_offsets.get(gain.tax_bucket, ZERO) + amount
        offset_rows.append({"loss_id": loss.loss_id, "gain_id": gain.gain_id,
                            "loss_event_id": loss.source_event_id, "loss_lot_id": loss.lot_id,
                            "gain_event_id": gain.source_event_id, "gain_lot_id": gain.lot_id,
                            "amount_inr": str(amount), "tax_bucket": gain.tax_bucket})

    buckets = ("section76", "section196", "section197", "section198")
    gross = {bucket: sum((g.amount_inr for g in gain_by_id.values() if g.tax_bucket == bucket), ZERO)
             for bucket in buckets}
    offsets_by_bucket = {bucket: bucket_offsets.get(bucket, ZERO) for bucket in buckets}
    candidate = {bucket: gross[bucket] - offsets_by_bucket[bucket] for bucket in buckets}
    unallocated: dict[str, Decimal] = {}
    carryforward: dict[str, Decimal] = {}
    loss_trace = []
    for loss in loss_by_id.values():
        remaining = loss.amount_inr - used_by_loss.get(loss.loss_id, ZERO)
        if remaining:
            unallocated[loss.loss_id] = remaining
            origin = _tax_year_start(loss.origin_tax_year)
            eligible = loss.return_filed_under_263_1 and year - origin < 8
            if eligible:
                carryforward[loss.loss_id] = remaining
        loss_trace.append({
            "loss_id": loss.loss_id, "source_event_id": loss.source_event_id,
            "lot_id": loss.lot_id, "origin_tax_year": loss.origin_tax_year,
            "character": loss.character, "gross_loss_inr": str(loss.amount_inr),
            "used_in_tax_year_inr": str(used_by_loss.get(loss.loss_id, ZERO)),
            "remaining_loss_inr": str(remaining),
            "return_evidence_reference": loss.return_evidence_reference or None,
            "carryforward_eligible": bool(remaining and loss.return_filed_under_263_1
                                          and year - _tax_year_start(loss.origin_tax_year) < 8),
        })
    return ScheduleResult(tax_year, gross, offsets_by_bucket, candidate, loss_trace,
                          offset_rows, unallocated, carryforward, tax_application_allowed=False)
