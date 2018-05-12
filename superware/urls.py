# -*- coding: utf-8 -*-
from django.conf.urls import url

from superware import views

app_name = 'superware'

urlpatterns = [
    #url(r'^registrarse/$', views.registrarse, name='registrarse'), #nombre para identificar en html
    #url(r'^usuario_login/$', views.usuario_login, name="usuario_login"),
    url(r'^login/$', views.usuario_login, name="login"),
    url(r'^logout/$', views.usuario_logout, name="logout"),
    url(r'^consultas/$', views.consultas, name="consultas"),
    url(r'^ventas/$', views.index, name="ventas"),
    url(r'^inventario/$', views.listarInventario, name="listarInventario"),
    url(r'^agregarArticulo/$', views.agregarArticulo, name="agregarArticulo"),
    url(r'^respaldos/$', views.menuRespaldos, name="menuRespaldos"),
    url(r'^nuevoRespaldo/$', views.crearRespaldo, name="crearRespaldo"),
    url(r'^restaurarUltimo/$', views.restaurarUltimo, name="restaurarUltimo"),
    url(r'^editarArticulo/(?P<idarticulo>\w+)/$', views.editarArticulo, name="editarArticulo"),
    url(r'^eliminarArticulo/(?P<idarticulo>\w+)/$', views.eliminarArticulo, name="eliminarArticulo"),

]