from __future__ import annotations


FACT_KIND_ORDERABLE_CASH = "kb_ssqm0004_orderable_cash"
FACT_KIND_DEPOSIT_TODAY = "kb_ssqm0004_deposit_today"
FACT_KIND_DEPOSIT_D1 = "kb_ssqm0004_deposit_d1"
FACT_KIND_DEPOSIT_D2 = "kb_ssqm0004_deposit_d2"
FACT_KIND_WITHDRAWABLE_CASH = "kb_ssqm0004_withdrawable_cash"
FACT_KIND_ORDERABLE_TOTAL = "kb_ssqm0004_orderable_total"
FACT_KIND_POSITION_MARKET_VALUE = "kb_ssqm2952_position_market_value"
FACT_KIND_BROKER_REPORTED_ACCOUNT_VALUATION = (
    "kb_ssqm2952_broker_reported_account_valuation"
)

BROKER_FIELD_ORDERABLE_CASH = "ordr_psbl_csh"
BROKER_FIELD_DEPOSIT_TODAY = "tdy_tfnd_amt"
BROKER_FIELD_DEPOSIT_D1 = "ndy_tfnd"
BROKER_FIELD_DEPOSIT_D2 = "nxt2_dy_tfnd"
BROKER_FIELD_WITHDRAWABLE_CASH = "do_psbl_csh"
BROKER_FIELD_ORDERABLE_TOTAL = "ordr_psbl_amt"
BROKER_FIELD_POSITION_MARKET_VALUE = "val_amt"
BROKER_FIELD_ACCOUNT_VALUATION = "nt_asts_val_amt"

AMOUNT_PRESENCE_PRESENT = "present"
AMOUNT_PRESENCE_MISSING = "missing"

SIZING_AUTHORITY_NONE = "NOT_SIZING_AUTHORITY"
DOMESTIC_CURRENCY_CODE = "KRW"

# Fields that must never be substituted for OrderableCashFact.
FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_FIELDS = frozenset(
    {
        "tdy_tfnd_amt",
        "ndy_tfnd",
        "nxt2_dy_tfnd",
        "dy_tfnd",
        "do_psbl_csh",
        "do_psbl_sbt",
        "do_psbl_tl_amt",
        "ordr_psbl_amt",
        "ordr_psbl_sbt",
        "ordr_std_dpstn_csh",
        "ordr_std_dpstn_sbt",
        "ordr_std_dpstn_tl_amt",
        "nt_asts_val_amt",
        "val_amt",
        "val_amt_sum",
        "scrts_nt_val_amt",
        "crdt_ordr_psbl_csh",
        "crdt_ordr_psbl_sbt",
        "crdt_ordr_psbl_tl_amt",
        "fncng_amt",
        "gnl_ln_amt",
        "nrfnd_fncng_amt",
        "mx_ordr_psbl_csh",
        "mx_ordr_psbl_amt",
        "mx_do_psbl_csh",
        "mx_buy_psbl_amt",
    }
)

FORBIDDEN_ORDERABLE_CASH_SUBSTITUTE_PREFIXES = (
    "mx_",
    "crdt_",
    "fncng_",
    "ln_",
)

LEVERAGE_INFLATION_FIELDS = frozenset(
    {
        "ordr_psbl_sbt",
        "ordr_psbl_amt",
        "do_psbl_sbt",
        "do_psbl_tl_amt",
        "crdt_ordr_psbl_csh",
        "crdt_ordr_psbl_tl_amt",
        "mx_ordr_psbl_csh",
        "mx_ordr_psbl_amt",
        "mx_do_psbl_csh",
        "mx_buy_psbl_amt",
        "fncng_amt",
        "gnl_ln_amt",
    }
)
