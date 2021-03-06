import os
from datetime import timedelta
from unittest.mock import patch

from django.test import TestCase
from django.utils import timezone

from app.models import StatLog, Profile, Post, TempData
from app.services import stat_service
from app.services.stat_service import RunnerDto, StatDto
from app.tests import TESTS_DIR, create_config, create_runnings, create_date
from app.util import date_to_js_unix_time


class StatServiceTests(TestCase):

    def test_calc_stat_without_data(self):
        """Test that raised exception if no data in DB"""
        with self.assertRaises(Post.DoesNotExist):
            stat_service.calc_stat(StatLog.StatType.DISTANCE, None, None)

    def test_calc_stat_without_params(self):
        """Test that test_calc_stat raises RuntimeError without params"""
        create_runnings()
        with self.assertRaises(RuntimeError):
            stat_service.calc_stat(None, None, None)

        """Test without start distance"""
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, None, 100)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertIsNone(stat.start_distance)
        self.assertEqual(stat.end_distance, 100)
        self.assertEqual(stat.start_date, create_date(2015, 9, 1, 3, 56, 9))
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 3, 22, 14))

        """Test without end distance"""
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, 16, None)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertEqual(stat.start_distance, 16)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 2, 2, 56, 41))
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 7, 12, 15))

        """Test without start date"""
        start_date = None
        end_date = create_date(2015, 9, 3)
        end_range = date_to_js_unix_time(end_date)
        stat = stat_service.calc_stat(StatLog.StatType.DATE, start_date, end_range)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 1, 3, 56, 9))
        self.assertEqual(stat.end_date, create_date(2015, 9, 3, 23, 59, 59))

        """Test without end date"""
        start_date = create_date(2015, 9, 3, 4, 38, 2)
        end_date = None
        start_range = date_to_js_unix_time(start_date)
        stat = stat_service.calc_stat(StatLog.StatType.DATE, start_range, end_date)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, start_date)
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 7, 12, 15))

    def test_calc_stat_all_time(self):
        """Test that stat is right for whole time"""
        create_runnings()
        stat = stat_service.calc_stat(StatLog.StatType.DATE, None, None)

        max_one_man_distance = RunnerDto(Profile.objects.get(pk=63399502), 2, 20)
        max_one_man_training_count = max_one_man_distance
        top_all_runners = [
            RunnerDto(Profile.objects.get(pk=63399502), 2, 20),
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=8429458), 1, 12),
            RunnerDto(Profile.objects.get(pk=2437792), 2, 9),
            RunnerDto(Profile.objects.get(pk=39752943), 2, 9)
        ]
        top_int_runners = top_all_runners
        new_runners = list(Profile.objects.exclude(pk=-1013265).order_by('join_date'))

        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 1, 3, 56, 9))
        self.assertEqual(stat.end_date, create_date(2015, 9, 4, 7, 12, 15))
        self.assertEqual(stat.all_days_count, 4)
        self.assertEqual(stat.interval_days_count, 4)
        self.assertEqual(stat.max_one_man_distance, max_one_man_distance)
        self.assertEqual(stat.all_training_count, 20)
        self.assertEqual(stat.max_one_man_training_count, max_one_man_training_count)
        self.assertEqual(stat.all_runners_count, 15)
        self.assertEqual(stat.new_runners, new_runners)
        self.assertEqual(stat.new_runners_count, 15)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_int_runners)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertAlmostEqual(stat.distance_per_day, 28, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.6, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 5, 2)

    def test_calc_stat_for_dates(self):
        """Test that stat is right between 2 dates"""
        create_runnings()

        start_date = create_date(2015, 9, 2)
        end_date = create_date(2015, 9, 3)

        stat = stat_service.calc_stat(
            StatLog.StatType.DATE,
            start_range=date_to_js_unix_time(start_date),
            end_range=date_to_js_unix_time(end_date)
        )

        max_one_man_distance = RunnerDto(Profile.objects.get(pk=117963335), 1, 16)
        max_one_man_training_count = RunnerDto(Profile.objects.get(pk=39752943), 2, 9)

        top_all_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=8429458), 1, 12),
            RunnerDto(Profile.objects.get(pk=39752943), 2, 9),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6)
        ]

        top_interval_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6),
            RunnerDto(Profile.objects.get(pk=11351451), 1, 5),
            RunnerDto(Profile.objects.get(pk=39752943), 1, 5)
        ]

        self.assertIsNone(stat.start_distance)
        self.assertIsNone(stat.end_distance)
        self.assertEqual(stat.start_date, start_date)
        self.assertEqual(stat.end_date, create_date(2015, 9, 3, 23, 59, 59))
        self.assertEqual(stat.all_days_count, 3)
        self.assertEqual(stat.interval_days_count, 2)
        self.assertEqual(stat.all_distance, 77)
        self.assertEqual(stat.max_one_man_distance, max_one_man_distance)
        self.assertEqual(stat.all_training_count, 13)
        self.assertEqual(stat.max_one_man_training_count, max_one_man_training_count)
        self.assertEqual(stat.all_runners_count, 12)
        self.assertEqual(stat.interval_runners_count, 11)
        self.assertEqual(len(stat.new_runners), 10)
        self.assertEqual(stat.new_runners_count, 10)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_interval_runners)
        self.assertEqual(stat.type, StatLog.StatType.DATE)
        self.assertAlmostEqual(stat.distance_per_day, 25.67, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.92, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 4.33, 2)

    def test_calc_stat_for_distances(self):
        """Test that stat is right between 2 distances"""
        create_runnings()

        start_distance = 16
        end_distance = 77

        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, start_distance, end_distance)
        self.assertIsNotNone(stat)

        max_one_man_distance = RunnerDto(Profile.objects.get(pk=117963335), 1, 16)
        max_one_man_training_count = RunnerDto(Profile.objects.get(pk=39752943), 2, 9)

        top_all_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=8429458), 1, 12),
            RunnerDto(Profile.objects.get(pk=39752943), 2, 9),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6)
        ]

        top_interval_runners = [
            RunnerDto(Profile.objects.get(pk=117963335), 1, 16),
            RunnerDto(Profile.objects.get(pk=63399502), 1, 8),
            RunnerDto(Profile.objects.get(pk=10811344), 1, 6),
            RunnerDto(Profile.objects.get(pk=11351451), 1, 5),
            RunnerDto(Profile.objects.get(pk=39752943), 1, 5)
        ]

        self.assertEqual(stat.start_distance, start_distance)
        self.assertEqual(stat.end_distance, end_distance)
        self.assertEqual(stat.start_date, create_date(2015, 9, 2, 2, 56, 41))
        self.assertEqual(stat.end_date, create_date(2015, 9, 3, 17, 16, 16))
        self.assertEqual(stat.all_days_count, 3)
        self.assertEqual(stat.interval_days_count, 2)
        self.assertEqual(stat.all_distance, 77)
        self.assertEqual(stat.max_one_man_distance, max_one_man_distance)
        self.assertEqual(stat.all_training_count, 13)
        self.assertEqual(stat.max_one_man_training_count, max_one_man_training_count)
        self.assertEqual(stat.all_runners_count, 12)
        self.assertEqual(stat.interval_runners_count, 11)
        self.assertEqual(len(stat.new_runners), 10)
        self.assertEqual(stat.new_runners_count, 10)
        self.assertEqual(stat.top_all_runners, top_all_runners)
        self.assertEqual(stat.top_interval_runners, top_interval_runners)
        self.assertEqual(stat.type, StatLog.StatType.DISTANCE)
        self.assertAlmostEqual(stat.distance_per_day, 25.67, 2)
        self.assertAlmostEqual(stat.distance_per_training, 5.92, 2)
        self.assertAlmostEqual(stat.training_count_per_day, 4.33, 2)

    def test_create_stat_log(self):
        """Test that create_stat_log return correct values"""
        create_runnings()
        stat = stat_service.calc_stat(StatLog.StatType.DATE, None, None)

        stat_log = stat.create_stat_log(100)
        self.assertIsNone(stat_log.id)
        self.assertEqual(stat_log.post_id, 100)
        self.assertEqual(stat_log.stat_type, StatLog.StatType.DATE)
        self.assertEqual(stat_log.start_value, '2015-09-01')
        self.assertEqual(stat_log.end_value, '2015-09-04')

        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, 100, 200)
        stat_log = stat.create_stat_log(200)
        self.assertIsNone(stat_log.id)
        self.assertEqual(stat_log.post_id, 200)
        self.assertEqual(stat_log.stat_type, StatLog.StatType.DISTANCE)
        self.assertEqual(stat_log.start_value, '100')
        self.assertEqual(stat_log.end_value, '200')

    def test_get_stat(self):
        """Test that get_stat return correct values"""
        stat = stat_service.get_stat()
        self.assertEqual(stat, {
            'distance_sum': 0,
            'running_count': 0,
            'post_count': 0
        })

        create_runnings()
        stat = stat_service.get_stat()
        self.assertEqual(stat, {
            'distance_sum': 112,
            'running_count': 20,
            'post_count': 21
        })

    def test_update_stat(self):
        """Test that update stat correct update last_sync_date"""
        temp_data = TempData.objects.get()
        temp_data.last_sync_date = timezone.now() - timedelta(days=100)

        before_date = timezone.now()
        stat_service.update_stat()
        after_date = timezone.now()
        temp_data.refresh_from_db()

        self.assertGreaterEqual(temp_data.last_sync_date, before_date)
        self.assertLessEqual(temp_data.last_sync_date, after_date)

    @patch('app.services.vk_api_service.create_post', return_value={'post_id': 123})
    @patch('app.services.stat_service._create_post_text', return_value='Post text')
    def test_interval_publish_stat_post(self, create_text, create_post):
        """Test that stat is publishing through interval"""
        with self.settings(PUBLISHING_STAT_INTERVAL=50):
            stat_service.interval_publish_stat_post()
            self.assertEqual(create_text.call_count, 0)
            self.assertEqual(create_post.call_count, 0)

            create_runnings()
            stat_service.interval_publish_stat_post()
            last_stat_log = StatLog.objects.last()
            self.assertEqual(create_text.call_count, 1)
            self.assertEqual(create_post.call_count, 1)
            self.assertEqual(create_post.call_args.args, ('Post text',))
            self.assertEqual(last_stat_log.stat_type, StatLog.StatType.DISTANCE)
            self.assertEqual(last_stat_log.start_value, '0')
            self.assertEqual(last_stat_log.end_value, '50')

            stat_service.interval_publish_stat_post()
            last_stat_log = StatLog.objects.last()
            self.assertEqual(create_text.call_count, 2)
            self.assertEqual(create_post.call_count, 2)
            self.assertEqual(create_post.call_args.args, ('Post text',))
            self.assertEqual(last_stat_log.stat_type, StatLog.StatType.DISTANCE)
            self.assertEqual(last_stat_log.start_value, '50')
            self.assertEqual(last_stat_log.end_value, '100')

            stat_service.interval_publish_stat_post()
            self.assertEqual(create_text.call_count, 2)
            self.assertEqual(create_post.call_count, 2)

    @patch('app.services.vk_api_service.create_post', return_value={'post_id': 123})
    @patch('app.services.stat_service._create_post_text', return_value='Post text')
    def test_publish_stat_post(self, create_text, create_post):
        """Test that stat is publishing"""
        stat = StatDto(start_distance=1000, end_distance=2000)
        post_id = stat_service.publish_stat_post(stat)
        self.assertEqual(post_id, 123)
        self.assertEqual(create_text.call_count, 1)
        self.assertEqual(create_post.call_count, 1)
        self.assertEqual(create_post.call_args.args, ('Post text',))

        stat_log = StatLog.objects.last()
        self.assertEqual(StatLog.objects.count(), 1)
        self.assertEqual(stat_log.start_value, '1000')
        self.assertEqual(stat_log.end_value, '2000')

    def test_create_post_text(self):
        """Test that stat text is correct for distance segment"""
        self.maxDiff = None
        create_runnings()
        create_config()

        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, 50, 100)
        stat.new_runners_count = 5
        text = stat_service._create_post_text(stat)
        with open(os.path.join(TESTS_DIR, 'data', 'stat_1.txt')) as f:
            self.assertEqual(text, f.read())

        """Test that stat text is correct for date segment"""
        stat.create_stat_log('123').save()

        stat = stat_service.calc_stat(StatLog.StatType.DATE, None, None)
        text = stat_service._create_post_text(stat)
        with open(os.path.join(TESTS_DIR, 'data', 'stat_2.txt')) as f:
            self.assertEqual(text, f.read())

        """Test that stat text is correct without new runners"""
        stat = stat_service.calc_stat(StatLog.StatType.DISTANCE, 90, 100)
        self.assertEqual(stat.new_runners_count, 0)
        text = stat_service._create_post_text(stat)
        with open(os.path.join(TESTS_DIR, 'data', 'stat_3.txt')) as f:
            self.assertEqual(text, f.read())
