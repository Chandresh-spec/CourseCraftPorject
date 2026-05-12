from rest_framework.pagination import PageNumberPagination



class CoursePagination(PageNumberPagination):
    page_size=6
    max_page_size=50

