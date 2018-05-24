from django.conf import settings
from django.conf.urls import url, include
from django.conf.urls.static import static
from django.contrib import admin

from superware import views, serilizer

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^$',views.index, name="index"),
    url(r'^application/', include('superware.urls')),

    url(r'^articulos/$', serilizer.listaArticulos, name="listaArticulos"),
    url(r'^obtenerArticulo/$', serilizer.getArticulo, name="getArticulo"),

]


urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)