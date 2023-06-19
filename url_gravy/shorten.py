import short_url
import os

from sqlalchemy.exc import IntegrityError

from sam_core.database import Session, supply_session

from url_gravy import crud


class URLNotAvailableError(Exception):
    pass

@supply_session
def execute(target: str, suffix: str=None, db: Session=None) -> str:
    """
    Generate a shortened URL which redirects to the user's chosen resource.
    :param target: the URL which the new URL should redirect to.
    :param suffix: a user-defined suffix to use (or None).
    :return: the shortened URL.
    """
    if suffix is not None:
        if not validate_user_suffix(suffix):
            # True if the user-defined suffix is inside the set of possible
            # auto-generated suffixes.
            raise URLNotAvailableError
    else:
        suffix = generate_suffix(db=db)
    try:
        crud.create_redirect(target, suffix, db=db)
    except IntegrityError:
        # True if the suffix uniqueness constraint was violated
        raise URLNotAvailableError

    return os.environ["APP_HOST"] + ':' + os.environ["APP_PORT"] + '/' + suffix

def validate_user_suffix(suffix: str) -> bool:
    """
    Check that a user suffix is outside the set of auto-generated suffixes.
    :param suffix: a user-defined suffix.
    :return: True if the suffix is viable otherwise False.
    """
    if len(suffix) != int(os.environ["AUTO_SUFFIX_LEN"]):
        # True if a different length to automatically-generated suffixes
        return True
    try:
        short_url.decode_url(suffix)
    except ValueError:
        # True if the suffix cannot be decoded to an integer base
        return True
    return False

@supply_session
def generate_suffix(db: Session=None) -> str:
    """
    Generate a new suffix from its corresponding database id value.
    :param db: a live database session.
    :return: an alphanumeric suffix of AUTO_SUFFIX_LEN characters.
    """
    last_record = crud.get_last_redirect(db=db)

    new_id = 1  # Default to the starting id
    if last_record is not None:
        new_id = last_record.id + 1

    return short_url.encode_url(new_id, int(os.environ["AUTO_SUFFIX_LEN"]))
