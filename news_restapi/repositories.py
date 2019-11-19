import sqlite3
from pathlib import Path, PurePath
from typing import List, Any, Tuple
from datetime import datetime

from .models import News, Comment
from .utils import datetime_to_timestamp, timestamp_to_datetime


def get_connection():
    db_path = Path(__file__).parent.parent / PurePath('db/news.db')
    return sqlite3.connect(db_path, isolation_level=None)


class RepositoryException(Exception):
    def __init__(self, message, *errors):
        super().__init__(message)
        self._errors = errors


class Repository:
    """
    A Base repository class for storing objects in a database table
    """
    def __init__(self, table_name: str, columns: Tuple[str, ...], connection=None):
        self.table_name = table_name
        self.columns = columns
        if connection:
            self.conn = connection
        else:
            try:
                self.conn = get_connection()
            except Exception as e:
                raise RepositoryException(*e.args)
        self._complete = False

    def __enter__(self):
        return self

    def __exit__(self, type_, value, traceback):
        self.close()

    def complete(self):
        self._complete = True

    def close(self):
        if self.conn:
            try:
                if self._complete:
                    self.conn.commit()
                else:
                    self.conn.rollback()
            except Exception as e:
                raise RepositoryException(*e.args)
            finally:
                try:
                    self.conn.close()
                except Exception as e:
                    raise RepositoryException(*e.args)

    def add(self, obj: Any) -> Any:
        """
        Inserts a given object to a table
        :param obj: object to store
        :return: same object with id
        """
        try:
            cursor = self.conn.cursor()
            data = self.obj_to_data(obj)
            query = 'INSERT INTO {} ({}) VALUES(?, ?, ?, ?)'.format(
                self.table_name, self.columns_as_string
            )
            cursor.execute(query, data)
            obj.id = cursor.lastrowid
            return obj
        except Exception as e:
            raise RepositoryException('Error storing object: {}'.format(e), e)

    def list(self, limit: int, offset: int) -> List:
        """
        Fetches a given amount of objects from a table
        :param limit:
        :param offset:
        :return: a list of objects
        """
        try:
            cursor = self.conn.cursor()
            query = 'SELECT {} FROM {} ORDER BY id DESC LIMIT {} OFFSET {}'.format(
                'id,{}'.format(self.columns_as_string), self.table_name, limit, offset
            )
            cursor.execute(query)
            return [self.data_to_obj(data) for data in cursor.fetchall()]
        except Exception as e:
            raise RepositoryException('Error fetching objects: {}'.format(e), e)

    def get(self, id: int) -> Any:
        """
        Fetches an object from a table with given id
        :param id:
        :return: object
        """
        try:
            cursor = self.conn.cursor()
            query = 'SELECT {} FROM {} WHERE id = ? LIMIT 1'.format(
                'id,{}'.format(self.columns_as_string), self.table_name
            )
            cursor.execute(query, (id,))
            data = cursor.fetchone()
            return self.data_to_obj(data) if data else None
        except Exception as e:
            raise RepositoryException('Error fetching object: {}'.format(e), e)

    def update(self, obj: Any) -> Any:
        """
        Updates a given object in a table
        :param obj:
        :return: object
        """
        try:
            cursor = self.conn.cursor()
            data = self.obj_to_data(obj) + (obj.id,)
            columns = ','.join(['{}=?'.format(c) for c in self.columns])
            cursor.execute('UPDATE {} SET {} WHERE id = ?'.format(self.table_name, columns), data)
            return obj
        except Exception as e:
            raise RepositoryException('Error updating object: {}'.format(e), e)

    def delete(self, obj: Any) -> None:
        """
        Deletes a given object from a table
        :param obj:
        :return:
        """
        try:
            cursor = self.conn.cursor()
            cursor.execute('DELETE FROM {} WHERE id = ?'.format(self.table_name), (obj.id,))
            return None
        except Exception as e:
            raise RepositoryException('Error deleting object: {}'.format(e), e)

    @property
    def columns_as_string(self) -> str:
        return ','.join(self.columns)

    def obj_to_data(self, obj: Any) -> tuple:
        raise NotImplementedError()

    def data_to_obj(self, data: tuple) -> Any:
        raise NotImplementedError()


class NewsRepository(Repository):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'news',
            ('created_date', 'modified_date', 'title', 'content'),
            *args, **kwargs
        )

    def obj_to_data(self, obj: News) -> tuple:
        return (
            datetime_to_timestamp(obj.created_date),
            datetime_to_timestamp(obj.modified_date),
            obj.title,
            obj.content
        )

    def data_to_obj(self, data: tuple) -> News:
        return News(
            id=data[0],
            created_date=timestamp_to_datetime(data[1]),
            modified_date=timestamp_to_datetime(data[2]),
            title=data[3],
            content=data[4]
        )

    def add_news(self, news: News) -> News:
        return self.add(news)

    def list_news(self, limit: int, offset: int) -> List:
        return self.list(limit, offset)

    def get_news(self, id: int) -> News:
        return self.get(id)

    def update_news(self, obj: News) -> News:
        obj.modified_date = datetime.now()
        return self.update(obj)

    def delete_news(self, obj: News) -> None:
        return self.delete(obj)


class CommentRepository(Repository):
    def __init__(self, *args, **kwargs):
        super().__init__(
            'comment',
            ('created_date', 'modified_date', 'news_id', 'content'),
            *args, **kwargs
        )

    def obj_to_data(self, obj: Comment) -> tuple:
        return (
            datetime_to_timestamp(obj.created_date),
            datetime_to_timestamp(obj.modified_date),
            obj.news_id,
            obj.content
        )

    def data_to_obj(self, data: tuple) -> Comment:
        return Comment(
            id=data[0],
            created_date=timestamp_to_datetime(data[1]),
            modified_date=timestamp_to_datetime(data[2]),
            news_id=data[3],
            content=data[4]
        )

    def add_comment(self, comment: Comment) -> Comment:
        return self.add(comment)

    def list_comment(self, limit: int, offset: int) -> List:
        return self.list(limit, offset)

    def get_comment(self, id: int) -> Comment:
        return self.get(id)

    def get_comments_for_news(self, news_id: int, limit: int, offset: int) -> List:
        """
        Fetches a list of comments that corresponds to the given news id
        :param news_id:
        :param limit:
        :param offset:
        :return:
        """
        try:
            cursor = self.conn.cursor()
            query = 'SELECT {} FROM {} WHERE news_id = ? ORDER BY id DESC LIMIT {} OFFSET {}'.format(
                'id,{}'.format(self.columns_as_string), self.table_name, limit, offset
            )
            cursor.execute(query, (news_id,))
            return [self.data_to_obj(data) for data in cursor.fetchall()]
        except Exception as e:
            raise RepositoryException('Error fetching objects: {}'.format(e), e)

    def update_comment(self, obj: Comment) -> Comment:
        obj.modified_date = datetime.now()
        return self.update(obj)

    def delete_comment(self, comment: Comment) -> None:
        return self.delete(comment)
