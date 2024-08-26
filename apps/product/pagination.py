from rest_framework.pagination import PageNumberPagination
from django.utils.translation import gettext_lazy as _


class DynamicPageNumberPagination(PageNumberPagination):
    page_size_query_param = 'page_size'

    def get_page_size(self, request):
        if hasattr(request, 'user_agent') and request.user_agent.is_mobile:
            return max(min(int(request.query_params.get('page_size', 6)), 12), 6)
        else:
            return max(min(int(request.query_params.get('page_size', 12)), 24), 12)
