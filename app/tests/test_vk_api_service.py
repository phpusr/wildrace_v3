import os

from django.test import TestCase

from app.models import Config
from app.services import vk_api_service


def create_config():
    return Config.objects.create(
        id=1,
        sync_posts=False,
        sync_seconds=300,
        group_id=88923650,
        group_short_link='',
        commenting=False,
        comment_access_token=os.getenv('ACCESS_TOKEN'),
        comment_from_group=False,
        publish_stat=False
    )


class VkApiTests(TestCase):

    def setUp(self):
        create_config()

    def test_authorize_url(self):
        """Test authorize url"""
        authorize_url = 'https://oauth.vk.com/authorize?client_id=5344865&display=page&' \
                        'redirect_uri=https://oauth.vk.com/blank.html&scope=wall,offline&response_type=token&' \
                        'v=5.92'
        self.assertEquals(vk_api_service.get_authorize_url(), authorize_url)

    def test_get_group_url(self):
        self.assertEquals(vk_api_service.get_group_url(), 'https://vk.com/club88923650')

    def test_get_post_url(self):
        self.assertEquals(vk_api_service.get_post_url(1226), 'https://vk.com/club88923650?w=wall-88923650_1226')

    def test_wall_get(self):
        """Test that wall.get return value"""
        result = vk_api_service.wall_get(0, 1)
        self.assertIn('count', result)
        self.assertIn('items', result)
