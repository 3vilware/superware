# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from superware.models import *
from django.core import serializers
from django.http import HttpResponse
from django.contrib.auth.hashers import make_password, check_password
import json
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt



def listaArticulos(request):
    listaArticulos = []
    articulos = Articulo.objects.all()

    for articulo in articulos:
        data = {"Nombre":articulo.nombre, "Descripcion":articulo.descripcion, "Categoria":str(articulo.categoria),
                "Precio":articulo.precio, "Stock":str(articulo.stock), "codigoBarras":str(articulo.codigoBarras),
                "Observaciones":articulo.observaciones} #FALTA FOTO
        listaArticulos.append(data)

    dataJson = json.dumps(listaArticulos)

    return HttpResponse(dataJson, content_type="application/json")


@csrf_exempt
def getArticulo(request):
    if request.method == 'POST':
        codigoBarras = request.POST.get('codigoBarras')
        try:
            articulo = Articulo.objects.get(codigoBarras=codigoBarras)
            data = {"Nombre":articulo.nombre, "Descripcion":articulo.descripcion, "Categoria":str(articulo.categoria),
                    "Precio":articulo.precio, "Stock":str(articulo.stock), "codigoBarras":str(articulo.codigoBarras),
                    "Observaciones":articulo.observaciones} #FALTA FOTO
            response = json.dumps(data)
        except ObjectDoesNotExist:
            response = json.dumps({"Error":"Does not exists"})

        return HttpResponse(response, content_type="application/json")


    else:
        return HttpResponse(json.dumps({"Error":"Bad Method"}), content_type="application/json" )


