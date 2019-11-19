from dataclasses import asdict
from datetime import datetime
from json import dumps

from news_restapi.models import News, Comment
from news_restapi import exceptions


class NewsController:
    """
    A controller that handles news request
    """
    def __init__(self, news_repository):
        self.news_repository = news_repository

    def validate_news(self, payload: dict) -> dict:
        """
        Validate input payload for required fields
        :param payload:
        :return: payload
        """
        errors = {}
        if not payload.get('title', None):
            errors['title'] = 'This field is required'
        if not payload.get('content', None):
            errors['content'] = 'This field is required'
        if errors:
            raise exceptions.ValidationError(dumps(errors))
        return payload

    def list_news(self, handler, **kwargs) -> list:
        """
        Get a list of news (25 for now)
        :param handler:
        :return: list of news
        """
        news_list = self.news_repository.list_news(25, 0)
        return [asdict(news) for news in news_list]

    def add_news(self, handler, **kwargs) -> dict:
        """
        Add new news
        :param handler:
        :return: added news
        """
        payload = self.validate_news(handler.get_payload())
        dt = datetime.now()
        news = News(id=None, created_date=dt, modified_date=dt, title=payload['title'], content=payload['content'])
        news = self.news_repository.add_news(news)
        return asdict(news)

    def get_news(self, handler, **kwargs) -> dict:
        """
        Get news by id
        :param handler:
        :return: news
        """
        news_id = kwargs.get('pk')
        news = self.news_repository.get_news(news_id)
        if not news:
            raise exceptions.NotFoundError()
        return asdict(news)

    def update_news(self, handler, **kwargs) -> dict:
        """
        Update news by id
        :param handler:
        :return:
        """
        news_id = kwargs.get('pk')
        news = self.news_repository.get_news(news_id)
        if not news:
            raise exceptions.NotFoundError()

        payload = self.validate_news(handler.get_payload())
        news.title = payload['title']
        news.content = payload['content']
        self.news_repository.update_news(news)
        return asdict(news)

    def delete_news(self, handler, **kwargs) -> dict:
        """
        Delete news by id
        :param handler:
        :return:
        """
        news_id = kwargs.get('pk')
        news = self.news_repository.get_news(news_id)
        if not news:
            raise exceptions.NotFoundError()

        self.news_repository.delete_news(news)
        return {}


class CommentController:
    """
    A controller that handles comments request
    """
    def __init__(self, comment_repository):
        self.comment_repository = comment_repository

    def validate_comment(self, payload: dict) -> dict:
        """
        Validate input payload for required fields
        :param payload:
        :return: payload
        """
        errors = {}
        if not payload.get('content', None):
            errors['content'] = 'This field is required'
        if errors:
            raise exceptions.ValidationError(dumps(errors))
        return payload

    def list_comments(self, handler, **kwargs) -> list:
        """
        Get a list of comments (25 for now)
        :param handler:
        :return: list of comments
        """
        news_id = kwargs['news_pk']
        comment_list = self.comment_repository.get_comments_for_news(news_id, 25, 0)
        return [asdict(comment) for comment in comment_list]

    def add_comment(self, handler, **kwargs) -> dict:
        """
        Add new comment
        :param handler:
        :return: added comment
        """
        payload = self.validate_comment(handler.get_payload())
        dt = datetime.now()
        news_id = kwargs['news_pk']
        comment = Comment(id=None, created_date=dt, modified_date=dt, news_id=news_id, content=payload['content'])
        comment = self.comment_repository.add_comment(comment)
        return asdict(comment)

    def get_comment(self, handler, **kwargs) -> dict:
        """
        Get comment by id
        :param handler:
        :return: comment
        """
        comment_id = kwargs.get('pk')
        comment = self.comment_repository.get_comment(comment_id)
        if not comment:
            raise exceptions.NotFoundError()
        return asdict(comment)

    def update_comment(self, handler, **kwargs) -> dict:
        """
        Update comment by id
        :param handler:
        :return:
        """
        comment_id = kwargs.get('pk')
        comment = self.comment_repository.get_comment(comment_id)
        if not comment:
            raise exceptions.NotFoundError()

        payload = self.validate_comment(handler.get_payload())
        comment.content = payload['content']
        self.comment_repository.update_comment(comment)
        return asdict(comment)

    def delete_comment(self, handler, **kwargs) -> dict:
        """
        Delete comment by id
        :param handler:
        :return:
        """
        comment_id = kwargs.get('pk')
        comment = self.comment_repository.get_comment(comment_id)
        if not comment:
            raise exceptions.NotFoundError()

        self.comment_repository.delete_comment(comment)
        return {}
