from PortfolioCapitalBucket.models import (
    ExplicitPortfolioCapitalBucket,
)


def validate_explicit_portfolio_capital_bucket(
    bucket: ExplicitPortfolioCapitalBucket,
) -> None:
    if type(bucket) is not ExplicitPortfolioCapitalBucket:
        raise TypeError(
            "bucket must be ExplicitPortfolioCapitalBucket"
        )
    if type(bucket.capital_bucket_id) is not str:
        raise TypeError("capital_bucket_id must be str")
    if bucket.capital_bucket_id.strip() == "":
        raise ValueError(
            "capital_bucket_id must not be blank"
        )
    if type(bucket.portfolio_id) is not str:
        raise TypeError("portfolio_id must be str")
    if bucket.portfolio_id.strip() == "":
        raise ValueError("portfolio_id must not be blank")
