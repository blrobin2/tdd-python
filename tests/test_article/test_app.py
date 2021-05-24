import json
import pathlib

import pytest
from jsonschema import validate, RefResolver
import requests

from blog.app import app
from blog.models import Article


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


def validate_payload(payload, schema_name):
    """
    Validate payload with selected schema
    """
    schemas_dir = str(
        f'{pathlib.Path(__file__).parent.absolute()}/schemas'
    )
    the_path: pathlib.Path = pathlib.Path(f'{schemas_dir}/{schema_name}')
    schema = json.loads(the_path.read_text())
    validate(
        payload,
        schema,
        resolver=RefResolver(
            'file://' + str(the_path.absolute()),
            schema
        )
    )


def test_create_article(client):
    """
    GIVEN request data for new article
    WHEN endpoint POST /articles is called
    THEN it should return Article in json format matching schema
    """
    data = dict(
        author='john@doe.com',
        title='New Article',
        content='Some extra awesome content'
    )
    response = client.post(
        '/articles',
        data=json.dumps(data),
        content_type='application/json'
    )

    validate_payload(response.json, 'Article.json')


def test_get_article(client):
    """
    GIVEN ID of article stored in the database
    WHEN endpoint GET /articles/<article-id> is called
    THEN it should return Article in json format matching schema
    """
    article = Article(
        author='jane@doe.com',
        title='New Article',
        content='Super extra awesome article'
    ).save()
    response = client.get(
        f'/articles/{article.id}',
        content_type='application/json'
    )

    validate_payload(response.json, 'Article.json')


def test_list_articles(client):
    """
    GIVEN articles stored in the database
    WHEN endpoint GET /articles is called
    THEN it should return list of Article in json format matching schema
    """
    Article(
        author='jane@doe.com',
        title='New Article',
        content='Super extra awesome content'
    ).save()
    response = client.get(
        '/articles',
        content_type='application/json'
    )

    validate_payload(response.json, 'ArticleList.json')


@pytest.mark.parametrize('data', [
    {
        'author': 'John Doe',
        'title': 'New Article',
        'content': 'Some extra awesome content'
    },
    {
        'author': 'John Doe',
        'title': 'New Article',
    },
    {
        'author': 'John Doe',
        'title': None,
        'content': 'Some content'
    }
])
def test_create_article_bad_request(client, data):
    """
    GIVEN request data with invalid values or missing attributes
    WHEN endpoint POST /articles is called
    THEN it should return status 400 and JSON body
    """
    response = client.post(
        '/articles',
        data=json.dumps(data),
        content_type='application/json',
    )

    assert response.status_code == 400
    assert response.json is not None


@pytest.mark.e2e
def test_create_list_get(client):
    requests.post('http://localhost:5000/articles', json={
        'author': 'john@doe.com',
        'title': 'New Article',
        'content': 'Some extra awesome content'
    })
    response = requests.get('http://localhost:5000/articles')
    article, *_ = response.json()

    response = requests.get(
        f'http://localhost:5000/articles/{article["id"]}'
    )

    assert response.status_code == 200
