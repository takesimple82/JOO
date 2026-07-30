from PortfolioDomain.models import PortfolioSubject


def validate_portfolio_subject(
    subject: PortfolioSubject,
) -> None:
    if type(subject) is not PortfolioSubject:
        raise TypeError("subject must be PortfolioSubject")

    if type(subject.subject_id) is not str:
        raise TypeError("subject_id must be str")
    if subject.subject_id.strip() == "":
        raise ValueError("subject_id must not be blank")

    if type(subject.display_name) is not str:
        raise TypeError("display_name must be str")
    if subject.display_name.strip() == "":
        raise ValueError("display_name must not be blank")
