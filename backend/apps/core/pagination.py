from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 200
    def get_paginated_response(self, data):
        return Response({'count': self.page.paginator.count,
                         'total_paginas': self.page.paginator.num_pages,
                         'pagina_atual': self.page.number,
                         'proxima': self.get_next_link(),
                         'anterior': self.get_previous_link(),
                         'resultados': data})

class LargePagination(PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000
    def get_paginated_response(self, data):
        return Response({'count': self.page.paginator.count, 'resultados': data})
