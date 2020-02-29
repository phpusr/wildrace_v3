import os
from typing import List

from django.templatetags.static import static
from djangorestframework_camel_case.render import CamelCaseJSONRenderer

from app import settings
from app.models import TempData
from app.serializers import FrontendDataSerializer
from app.services import stat_service, vk_api_service


def get_data(user):
    serializer = FrontendDataSerializer({
        'user': user if user.is_authenticated else None,
        'stat': stat_service.get_stat(),
        'last_sync_date': TempData.objects.get().last_sync_date.timestamp() * 1000,
        'config': {
            'project_version': settings.VERSION,
            'group_link': vk_api_service.get_group_url()
        }
    })

    data = {
        'google_analytics_id': settings.GOOGLE_ANALYTICS_ID,
        'frontend_data': CamelCaseJSONRenderer().render(serializer.data).decode('utf-8')
    }

    if settings.DEBUG:
        host = 'http://192.168.1.100:8080'
        data['js_files'] = [
            f'{host}/js/app.js',
            f'{host}/js/chunk-vendors.js'
        ]
        data['css_files'] = []
    else:
        data['js_files'] = _get_files('js', 'js')
        data['css_files'] = _get_files('css', 'css')

    return data


def _get_files(dir_name: str, ext: str) -> List[str]:
    path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static', dir_name)
    return [static(f'/{dir_name}/{f}') for f in os.listdir(path) if f.split('.')[-1] == ext]