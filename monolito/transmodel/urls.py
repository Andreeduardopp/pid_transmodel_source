from django.urls import path
from . import views

urlpatterns = [
    path("export/gtfs/", views.export_gtfs, name="transmodel-export-gtfs"),
    path("export/netex/", views.export_netex, name="transmodel-export-netex"),
    path("import/gtfs/", views.import_gtfs, name="transmodel-import-gtfs"),
]
