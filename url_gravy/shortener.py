import short_url
import re

from config import BASE_URL, AUTO_SUFFIX_LEN
from .database import Database, IntegrityError

class URLNotAvailableError(Exception):
    pass

class Shortener:
    """
    The Shortener class centralises the main shortening flow, including suffix
    validation/generation and db updating.
    """
    def execute(self, target: str, suffix: str=None) -> str:
        """
        Generate a shortened URL which redirects to the user's chosen resource.
        :param target: the URL which the new URL should redirect to.
        :param suffix: a user-defined suffix to use (or None).
        :return: the shortened URL.
        """
        if suffix is not None:
            if not self.validate_user_suffix(suffix):
                # True if the user-defined suffix is inside the set of possible
                # auto-generated suffixes.
                raise URLNotAvailableError
        else:
            suffix = self.generate_suffix()
        if not self.update_db(suffix, target):
            # True if the suffix uniqueness constraint was violated
            raise URLNotAvailableError

        return BASE_URL + '/' + suffix
    
    def validate_user_suffix(self, suffix: str) -> bool:
        """
        Check that a user suffix is outside the set of auto-generated suffixes.
        :param suffix: a user-defined suffix.
        :return: True if the suffix is viable otherwise False.
        """
        if len(suffix) != AUTO_SUFFIX_LEN:
            # True if a different length to automatically-generated suffixes
            return True
        try:
            short_url.decode_url(suffix)
        except ValueError:
            # True if the suffix cannot be decoded to an integer base
            return True
        return False
    
    def generate_suffix(self) -> str:
        """
        Generate a new suffix from its corresponding database id value.
        :return: an alphanumeric suffix of AUTO_SUFFIX_LEN characters.
        """
        last_record = Database().get_last_record()

        new_id = 1  # Default to the starting id
        if last_record is not None:
            new_id = last_record["id"] + 1

        return short_url.encode_url(new_id, AUTO_SUFFIX_LEN)
    
    def update_db(self, suffix: str, target: str) -> bool:
        """
        Update the database with a new record and indicate success.
        :param suffix: the new suffix value.
        :param target: the corresponding target URL.
        :return: False if the suffix is not unique otherwise True.
        """
        try:
            Database().create_record(suffix, target)
        except IntegrityError as exc:
            if re.match(r'Duplicate entry.+\.suffix', exc.msg):
                return False
        return True