from mysql import connector
from mysql.connector.errors import IntegrityError

from config import DB_SETTINGS

from .queries import *

FIELDS = ['id', 'suffix', 'target', 'created']

class Database:
    """
    The Database class is an interface for managing URL records.
    
    Connections are held open for as long as an instance is in scope - 
    avoid persisting longer than necessary.
    """
    def __init__(self) -> None:
        self.conn = connector.connect(**DB_SETTINGS)

    def create_record(self, suffix: str, target: str) -> None:
        """
        Store the suffix of a newly shortened URL and its target.
        :param suffix: a shortened URL suffix.
        :param target: a user-defined target URL. 
        """
        values = (suffix, target)
        with self.conn.cursor() as cursor:
            cursor.execute(CREATE_RECORD_SQL, values)
            self.conn.commit()
    
    def configure_tables(self) -> None:
        """
        Configure blank 'url' and 'urls_test' tables in the database.
        """
        for table_name in ['urls', 'urls_test']:
            query = CONFIGURE_TABLE_SQL.format(table_name=table_name)
            with self.conn.cursor() as cursor:
                cursor.execute(query)
    
    def delete_records(self, before_date: str=None) -> None:
        """
        Delete records from the 'urls' table.
        :param before_date: an upper date limit in the format 'YYYYMMDD'.
        """
        condition = ''
        if before_date is not None:
            condition = f'WHERE created < {before_date}'
        query = DELETE_RECORDS_SQL.format(condition=condition)
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            self.conn.commit()
    
    def get_records(self, **lkup) -> list:
        """
        Fetch all records which match the conditions set in lkup.
        :params lkup: a dictionary of field: value lookup values.
        :return: a list of matching records.
        """
        condition = ''
        if lkup:  # True if suffix/id/target values have been specified
            condition += 'WHERE '
            for key, value in lkup.items():
                condition += f'{key} = "{value}"'
        query = GET_RECORDS_SQL.format(condition=condition)
        with self.conn.cursor() as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
        return [self._index_record(x) for x in records]

    def _index_record(self, record: tuple) -> dict:
        return {k: v for k, v in zip(FIELDS, record)}
    
    def get_last_record(self) -> dict:
        """
        Fetch the most-recently added record from the urls table.
        :return: a dictionary of values indexed by field.
        """
        with self.conn.cursor() as cursor:
            cursor.execute(GET_LAST_RECORD_SQL)
            record = cursor.fetchone()
        if record is None:
            return record
        return self._index_record(record)