from __future__ import annotations

from datetime import datetime, timedelta, timezone

from ProviderGateway.models import (
    ExplicitBrokerAdapterBinding,
    ExplicitBrokerCollectRequest,
    ExplicitBrokerParameterProfile,
    ExplicitCollectOutcome,
    ExplicitProviderFailureSignal,
    ExplicitProviderPayloadEnvelope,
)

from KbCapitalFactAuthority.models import (
    ExplicitBalancesNormalizationRequest,
    ExplicitCapitalFactBinding,
    ExplicitCapitalFactPolicy,
    ExplicitCapitalPortfolioBinding,
    ExplicitCapitalSnapshotIdentity,
    ExplicitHoldingsCapitalNormalizationRequest,
    ExplicitPositionMarketValueBinding,
)


UTC = timezone.utc
COLLECTED = datetime(2026, 9, 26, 8, 0, tzinfo=UTC)
NOW = datetime(2026, 9, 26, 8, 5, tzinfo=UTC)


class FakeAdapter:
    def __init__(self, outcomes):
        if type(outcomes) is not dict:
            self._queue = list(outcomes)
            self._by_kind = None
        else:
            self._queue = None
            self._by_kind = dict(outcomes)
        self.calls = []

    def collect(self, request):
        self.calls.append(request)
        if self._by_kind is not None:
            return self._by_kind[request.request_kind]
        return self._queue.pop(0)


def binding(suffix, prefix):
    return ExplicitCapitalFactBinding(
        f"{prefix}-fact-{suffix}",
        f"{prefix}-envelope-{suffix}",
        None,
    )


def balances_request(suffix="001"):
    return ExplicitBalancesNormalizationRequest(
        f"balances-raw-{suffix}",
        "account-primary",
        "KRW",
        binding(suffix, "orderable-cash"),
        binding(suffix, "deposit-today"),
        binding(suffix, "deposit-d1"),
        binding(suffix, "deposit-d2"),
        binding(suffix, "withdrawable"),
        binding(suffix, "orderable-total"),
    )


def holdings_capital_request(suffix="001", *, symbol="005930", clsf="domestic-stock"):
    return ExplicitHoldingsCapitalNormalizationRequest(
        f"holdings-raw-{suffix}",
        "account-primary",
        binding(suffix, "account-valuation"),
        (
            ExplicitPositionMarketValueBinding(
                "account-primary",
                clsf,
                "KRW",
                symbol,
                f"position-mv-fact-{suffix}",
                f"position-mv-envelope-{suffix}",
                None,
            ),
        ),
    )


def balances_payload(
    *,
    orderable_cash="000000000339901",
    orderable_total="000000000339901",
    withdrawable="000000000000339901",
    deposit_today="000000001000000",
    deposit_d1="000000001000000",
    deposit_d2="000000000639950",
    extra=None,
):
    body = {
        "ordr_psbl_csh": orderable_cash,
        "ordr_psbl_amt": orderable_total,
        "do_psbl_csh": withdrawable,
        "tdy_tfnd_amt": deposit_today,
        "ndy_tfnd": deposit_d1,
        "nxt2_dy_tfnd": deposit_d2,
        "o_msg": "정상적으로 조회되었습니다.",
    }
    if extra:
        body.update(extra)
    return {
        "dataHeader": {
            "processFlag": "A",
            "processCode": "0011",
        },
        "dataBody": body,
    }


def holdings_payload(
    *,
    quantity="000000000000000",
    val_amt="000000000000426500",
    now_prc="0000000426500.00",
    currency="KRW",
    symbol="005930",
    clsf="domestic-stock",
    nt_asts="000000000001066450",
):
    return {
        "dataHeader": {
            "processFlag": "A",
            "processCode": "0011",
        },
        "dataBody": {
            "nt_asts_val_amt": nt_asts,
            "Record1": [
                {
                    "clsf": clsf,
                    "crncy_cd": currency,
                    "is_cd": symbol,
                    "hld_q": quantity,
                    "now_prc": now_prc,
                    "val_amt": val_amt,
                }
            ],
        },
    }


def success_outcome(envelope_id, correlation, payload, collected=COLLECTED):
    envelope = ExplicitProviderPayloadEnvelope(
        envelope_id,
        "kb_open_api",
        "broker_fact",
        collected,
        "success",
        payload,
        None,
        correlation,
    )
    return ExplicitCollectOutcome("success", envelope, None)


def failure_outcome():
    return ExplicitCollectOutcome(
        "failure",
        None,
        ExplicitProviderFailureSignal(
            "kb_open_api",
            COLLECTED,
            "UNAVAILABLE",
            None,
            "corr-fail",
        ),
    )


def balances_collect_request(suffix="001"):
    profile = ExplicitBrokerParameterProfile(
        f"profile-balances-{suffix}",
        "account-primary",
        ("balances", "holdings"),
    )
    adapter_binding = ExplicitBrokerAdapterBinding(
        "kb_open_api",
        "credential-ref",
        profile,
    )
    return ExplicitBrokerCollectRequest(
        f"balances-envelope-{suffix}",
        f"balances-corr-{suffix}",
        adapter_binding,
        "balances",
        None,
    )


def policy(seconds=3600):
    return ExplicitCapitalFactPolicy(timedelta(seconds=seconds))


def identity(suffix="001"):
    return ExplicitCapitalSnapshotIdentity(
        f"capital-snapshot-{suffix}",
        "account-primary",
    )


def portfolio_binding(suffix="001"):
    return ExplicitCapitalPortfolioBinding(
        f"portfolio-snapshot-{suffix}",
        f"portfolio-{suffix}",
        f"observation-{suffix}",
    )
