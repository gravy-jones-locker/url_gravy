import os
import typing

from sqlalchemy import select, create_engine, delete, Select
from datetime import date

from sam_core.database import supply_session, Session
from sam_core.database.getters import multi_getter

from url_gravy.models import Redirect


@supply_session
def get_last_redirect(db: Session=None) -> Redirect:
    """
    Return the most recently created redirect record.
    :return: the corresponding Redirect object.
    """
    return db.execute(
        select(Redirect). \
            order_by(Redirect.id.desc()). \
            limit(1)
    ).scalars().first()

@supply_session
def create_redirect(target: str, suffix: str, db: Session=None) -> Redirect:
    """
    Create a new redirect with the specified suffix/target url.
    :param target: the target url for the redirect.
    :param suffix: the desired custom suffix (e.g. google_pls).
    :return: the newly created Redirect object.
    """
    redirect = Redirect(suffix=suffix, target=target)
    db.add(redirect)
    db.commit()
    return redirect

@supply_session
def get_redirect_url(suffix: str, db: Session=None) -> typing.Optional[str]:
    """
    Get a redirect url from a corresponding suffix.
    :param suffix: the suffix to filter redirects against.
    :return: the target url for the given suffix (or None).
    """
    redirect = db.execute(
        select(Redirect). \
            filter(Redirect.suffix==suffix)
    ).scalars().first()
    if redirect is None:
        return None
    return redirect.target

@supply_session
def delete_redirects(before_date: str=None, db: Session=None) -> None:
    """
    Delete all redirects up to an optional date threshold.
    :before_date: an iso-format date threshold before which to delete records.
    """
    stmt = delete(Redirect)
    if before_date is not None:
        stmt = stmt.where(Redirect.created_on<date.fromisoformat(before_date))
    db.execute(stmt)
    db.commit()

@multi_getter(Redirect)
def get_redirects() -> Select:
    return select(Redirect)

def create_redirect_table() -> None:
    """
    Create db table to hold redirect records.
    """
    engine = create_engine(os.environ["DB_HOST"], echo=True)
    Redirect.metadata.create_all(engine)
