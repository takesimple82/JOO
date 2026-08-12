from dataclasses import dataclass


@dataclass(frozen=True)
class ExplicitMarketInstrument:
    instrument_id: str
