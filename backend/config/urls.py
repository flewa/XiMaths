from django.contrib import admin
from django.urls import path

from .api import api

# L'admin sert aux modérateurs : à leurs couleurs plutôt qu'à celles de Django.
admin.site.site_header = "XiMaths · modération"
admin.site.site_title = "XiMaths"
admin.site.index_title = "Administration"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]
