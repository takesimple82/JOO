from MarketInstrument.models import ExplicitMarketInstrument


def validate_explicit_market_instrument(
    instrument: ExplicitMarketInstrument,
) -> None:
    if type(instrument) is not ExplicitMarketInstrument:
        raise TypeError(
            "instrument must be ExplicitMarketInstrument"
        )
    if type(instrument.instrument_id) is not str:
        raise TypeError("instrument_id must be str")
    if instrument.instrument_id.strip() == "":
        raise ValueError(
            "instrument_id must not be blank"
        )
