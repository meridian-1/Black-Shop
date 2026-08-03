from django.contrib import admin
from django.urls import include, path
from django.conf.urls.static import static
from django.conf import settings
from schema_graph.views import Schema

urlpatterns = [
    path("admin/", admin.site.urls),
    path("cart/", include("apps.cart.urls")),
    # path("orders/", include("apps.orders.urls")),
    path("users/", include("apps.users.urls")),
    path("schema/", Schema.as_view(), name="schema"),
    path("", include("apps.main.urls")),
]

if settings.DEBUG:
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
