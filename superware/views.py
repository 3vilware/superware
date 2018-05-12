# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from rolepermissions.decorators import has_role_decorator
from superware.models import *
import os
from django.core import management
from django.conf import settings
from superware.forms import *
from django.db import transaction
from django.db import connections

# Create your views here.

@login_required
def index(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)
    return render(request,'ventas.html', {"usuario":empleado})

def usuario_login(request):
    if request.method == 'POST':
        usuario = request.POST.get('usuario')
        password = request.POST.get('pass')

        user = authenticate(username=usuario, password=password) #Es el modulo que autentifica

        if user:
            if user.is_active:
                login(request,user)
                url = reverse('index')
                return HttpResponseRedirect(url)
            else:
                return HttpResponse("Cuenta no activa")
        else:
            return HttpResponseRedirect(reverse('index'))
    else:
        return render(request, 'login.html',{})

@login_required
def usuario_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))

@login_required
def consultas(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    return render(request, 'consultas.html', {"usuario": empleado})


@login_required
def listarInventario(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    articulos = Articulo.objects.all()

    contexto =  {"usuario": empleado, "articulos":articulos}
    return render(request, 'inventario.html', contexto)


@transaction.atomic(using='default')
@login_required
def agregarArticulo(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    if request.method == 'POST':
        formArticulo = ArticuloForm(data=request.POST)
        if formArticulo.is_valid():
            with transaction.atomic():
                formArticulo.save()
                mensaje = "Transacción hecha correctamente"
                #REPLICA BDD MIRROR
                mirror = Articulo.objects.all().last()
                new = Articulo(nombre=mirror.nombre, categoria=mirror.categoria, observaciones=mirror.observaciones,
                               precio=mirror.precio, stock=mirror.stock, codigoBarras=mirror.codigoBarras,
                               descripcion=mirror.descripcion)
                new.save(using='matrix')

    else:
        form = ArticuloForm()
        mensaje = 0
        contexto = {"usuario": empleado, "form":form, "mensaje":mensaje}
        return render(request, 'agregarArticulo.html', contexto)

    articulos = Articulo.objects.all()

    contexto = {"usuario": empleado, "articulos": articulos, "mensaje":mensaje}
    return render(request, 'inventario.html', contexto)



@login_required
def editarArticulo(request, idarticulo):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    articulo = Articulo.objects.get(pk=idarticulo)

    if request.method == 'POST':
        formArticulo = ArticuloForm(data=request.POST, instance=articulo)
        if formArticulo.is_valid():
            print "EDITANDO CON INSTANCE"
            formArticulo.save()
    else:
        form = ArticuloForm(initial={'nombre':articulo.nombre, "categoria":articulo.categoria,
                                     "descripcion":articulo.descripcion, "observaciones":articulo.observaciones,
                                     "stock":articulo.stock, "precio":articulo.precio,
                                     "codigoBarras":articulo.codigoBarras})
        contexto = {"usuario": empleado, "form": form, "id":articulo.pk}
        return render(request, 'editarArticulo.html', contexto)

    articulos = Articulo.objects.all()

    contexto = {"usuario": empleado, "articulos": articulos}
    return render(request, 'inventario.html', contexto)



@login_required
def eliminarArticulo(request, idarticulo):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    articulo = Articulo.objects.get(pk=idarticulo)
    articulo.delete()

    articulos = Articulo.objects.all()
    contexto = {"usuario": empleado, "articulos": articulos}
    return render(request, 'inventario.html', contexto)

@has_role_decorator('sistemas')
@login_required
def menuRespaldos(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    contexto = {"usuario": empleado, "mensaje":0}
    return render(request, 'respaldos.html', contexto)

@has_role_decorator('sistemas')
@login_required
def crearRespaldo(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    management.call_command('dbbackup')
    print "Respaldo creado"
    contexto = {"usuario": empleado, "mensaje":1}
    return render(request, 'respaldos.html', contexto)

@login_required
def restaurarUltimo(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    management.call_command('dbrestore', '--noinput', '--database=default')  # con -i especifico nombre del archivo
    print "base de datos restaurada"
    contexto = {"usuario": empleado, "mensaje":1}
    return render(request, 'respaldos.html', contexto)