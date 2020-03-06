from unittest.mock import patch

from django.test import TestCase

from app.tests import create_config
from tasks.tasks import sync_posts_task, publish_stat_task


class TaskTests(TestCase):

    def setUp(self):
        self.config = create_config()

    def test_sync_posts_task_is_disabled(self):
        res = sync_posts_task()
        self.assertEqual(res, 'Sync posts task is disabled')

    def test_sync_posts_task_is_worked(self):
        self.config.sync_posts = True
        self.config.save()
        with patch('app.services.sync_service.sync_posts') as sp:
            res = sync_posts_task()
            self.assertEqual(sp.call_count, 1)
            self.assertEqual(res, 'Sync posts task successfully finished')

    def test_publish_stat_task_is_disabled(self):
        res = publish_stat_task()
        self.assertEqual(res, 'Publish stat task is disabled')

    def test_publish_stat_task_is_worked(self):
        self.config.publish_stat = True
        self.config.save()
        with patch('app.services.stat_service.interval_publish_stat_post') as psp:
            res = publish_stat_task()
            self.assertEqual(psp.call_count, 1)
            self.assertEqual(res, 'Publish stat task successfully finished')