from blog.models import Article
from blog.queries import ListArticlesQuery, GetArticleByIdQuery


def test_list_articles():
    """
    GIVEN 2 articles stored in the database
    WHEN the execute method is called
    THEN it should return 2 articles
    """

    Article(
        author='jane@doe.com',
        title='New Article',
        content='Good content'
    ).save()
    Article(
        author='jane@doe.com',
        title='Another Article',
        content='Even better content'
    ).save()

    query = ListArticlesQuery()

    assert len(query.execute()) == 2


def test_get_article_by_id():
    """
    Given ID of article stored in database
    WHEN the execute method is called on GetArticleByIdQuery with id set
    THEN it should return the articl with the same id
    """
    article = Article(
        author='jane@doe.com',
        title='New Article',
        content='Super extra awesome content'
    ).save()

    query = GetArticleByIdQuery(id=article.id)

    assert query.execute().id == article.id
