import sqlite3
import unittest
import copy

from pathlib import Path, PurePath
from datetime import datetime
from .utils import timestamp_to_datetime, datetime_to_timestamp
from .models import News, Comment
from .repositories import NewsRepository, CommentRepository


class TestCaseUtils(unittest.TestCase):
    def setUp(self):
        self.ts = 1573993663804000
        self.datetime = datetime(2019, 11, 17, 15, 27, 43, 804000)

    def test_timestamp_to_datetime(self):
        self.assertEqual(timestamp_to_datetime(self.ts), self.datetime)

    def test_datetime_to_timestamp(self):
        self.assertEqual(datetime_to_timestamp(self.datetime), self.ts)


class TestCaseBaseRepository(unittest.TestCase):
    def setUp(self):
        self.conn = sqlite3.connect(":memory:", isolation_level=None)
        cur = self.conn.cursor()

        with open(Path(__file__).parent.parent / PurePath('db/schema.sql'), 'r') as content_file:
            schema_sql = content_file.read()

        cur.executescript(schema_sql)
        self.conn.commit()


class TestCaseNewsRepository(TestCaseBaseRepository):
    def setUp(self):
        super().setUp()
        dt = datetime.now()
        self.news = News(id=None, created_date=dt, modified_date=dt, title='News title', content='News content')
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO news (created_date, modified_date, title, content) VALUES(?, ?, ?, ?)',
            (datetime_to_timestamp(self.news.created_date), datetime_to_timestamp(self.news.modified_date),
             self.news.title, self.news.content)
        )
        self.news.id = cur.lastrowid
        self.conn.commit()
        self.news_repository = NewsRepository(connection=self.conn)

    def test_list_news(self):
        news_list = self.news_repository.list_news(1, 0)
        self.assertListEqual(news_list, [self.news])

    def test_get_news(self):
        news = self.news_repository.get_news(self.news.id)
        self.assertEqual(news, self.news)

    def test_update_news(self):
        update_news = copy.copy(self.news)
        update_news.title = 'Updated title'
        self.news_repository.update_news(update_news)
        cur = self.conn.cursor()
        cur.execute('SELECT title FROM news WHERE id = ? LIMIT 1', (self.news.id,))
        data = cur.fetchone()
        self.assertEqual(update_news.title, data[0])

    def test_delete_news(self):
        self.news_repository.delete_news(self.news)
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM news WHERE id = ? LIMIT 1', (self.news.id,))
        data = cur.fetchone()
        self.assertIsNone(data)

    def test_add_news(self):
        created_news = self.news_repository.add_news(self.news)
        self.assertIsNotNone(created_news.id)


class TestCaseCommentRepository(TestCaseBaseRepository):
    def setUp(self):
        super().setUp()
        dt = datetime.now()
        self.news = News(id=None, created_date=dt, modified_date=dt, title='News title', content='News content')
        cur = self.conn.cursor()
        cur.execute(
            'INSERT INTO news (created_date, modified_date, title, content) VALUES(?, ?, ?, ?)',
            (datetime_to_timestamp(self.news.created_date), datetime_to_timestamp(self.news.modified_date),
             self.news.title, self.news.content)
        )
        self.news.id = cur.lastrowid

        self.comment = Comment(id=None, created_date=dt, modified_date=dt, news_id=self.news.id, content='Comment content')
        cur.execute(
            'INSERT INTO comment (created_date, modified_date, news_id, content) VALUES(?, ?, ?, ?)',
            (datetime_to_timestamp(self.comment.created_date), datetime_to_timestamp(self.comment.modified_date),
             self.comment.news_id, self.comment.content)
        )
        self.comment.id = cur.lastrowid
        self.comment_repository = CommentRepository(connection=self.conn)

    def test_list_comment(self):
        comment_list = self.comment_repository.get_comments_for_news(self.news, 1, 0)
        self.assertListEqual(comment_list, [self.comment])

    def test_get_comment(self):
        comment = self.comment_repository.get_comment(self.comment.id)
        self.assertEqual(comment, self.comment)

    def test_update_comment(self):
        update_comment = copy.copy(self.comment)
        update_comment.content = 'Updated content'
        self.comment_repository.update_comment(update_comment)
        cur = self.conn.cursor()
        cur.execute('SELECT content FROM comment WHERE id = ? LIMIT 1', (self.comment.id,))
        data = cur.fetchone()
        self.assertEqual(update_comment.content, data[0])

    def test_delete_comment(self):
        self.comment_repository.delete_comment(self.comment)
        cur = self.conn.cursor()
        cur.execute('SELECT id FROM comment WHERE id = ? LIMIT 1', (self.comment.id,))
        data = cur.fetchone()
        self.assertIsNone(data)

    def test_add_comment(self):
        created_comment = self.comment_repository.add_comment(self.comment)
        self.assertIsNotNone(created_comment.id)


