# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import threading
import time

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core import management
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.db import transaction
from django.http import HttpResponse, HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from rolepermissions.decorators import has_role_decorator

from superware.forms import *


# Create your views here.

@login_required
def index(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    listaArticulos = []
    lastDetalle = DetalleVenta.objects.last()
    articulosVenta = Venta.objects.filter(folio=lastDetalle.pk)
    total = 0
    band = False
    for a in articulosVenta:
        if band:
            listaArticulos.append(a.articulo)
            total = total+int(a.articulo.precio)
        band = True
    cantidad = len(listaArticulos)

    contexto = {"usuario":empleado, "articulos":listaArticulos, "cantidad":cantidad, "total":total}
    return render(request,'ventas.html', contexto)

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

    empleados = Empleado.objects.all()
    detalles = DetalleVenta.objects.all()

    contexto = {"usuario": empleado, "empleados":empleados, "detalles":detalles}
    return render(request, 'consultas.html', contexto)


@login_required
def listarInventario(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    newThread = threading.Thread(target=checkStock)
    newThread.start()

    articulos = Articulo.objects.all()

    contexto =  {"usuario": empleado, "articulos":articulos}
    return render(request, 'inventario.html', contexto)


@transaction.atomic(using='default')
@login_required
def agregarArticulo(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)
    if request.method == 'POST':
        print "Es post"
        formArticulo = ArticuloForm(request.POST, request.FILES)
        if formArticulo.is_valid():
            print "Es valido"
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
            print formArticulo.errors
            return render(request, 'agregarArticulo.html', {'form':formArticulo})

    else:
        print "se fue al else"
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
            #formArticulo.save(using='matrix')
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


@transaction.atomic()
@login_required
def eliminarArticulo(request, idarticulo):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    articulo = Articulo.objects.get(pk=idarticulo)
    with transaction.atomic():
        articulo.delete()
        articulo.delete(using='matrix')

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

def checkStock():
    print "ON!!"
    while True:
        articulos = Articulo.objects.all()
        for articulo in articulos:
            stock = articulo.stock

            if stock < 10:
                print "Deficiencia en el producto: ", articulo.nombre
                subject = 'AVISO de stock'
                message = ' El PRODUCTO' + articulo.nombre + 'SE ESTA AGOTANDO '
                email_from = settings.EMAIL_HOST_USER
                recipient_list = ['ricardo.amador@alumnos.udg.mx', ]
                send_mail(subject, message, email_from, recipient_list)
        time.sleep(600)

    return 1

# Arroja los datos a ventas
def agregarArticuloCarrito(request):
    barcode = request.GET.get('barcode')
    try:
        articulo = Articulo.objects.get(codigoBarras=barcode)
        if articulo.stock > 0:
            data = {"error":0, "nombreArticulo":articulo.nombre, "precio":str(articulo.precio),
                    "departamento":str(articulo.categoria.departamento), "categoria":str(articulo.categoria),
                    "observaciones":articulo.observaciones, "descripcion":articulo.descripcion,
                    "foto":articulo.foto.url, "stock":articulo.stock}
        else:
            data = {"error": 1, "message": "Sin stock!"}
    except ObjectDoesNotExist:
        data = {"error":1, "message": "No existe el articulo"}

    return JsonResponse(data)

@login_required
def addToCart(request):
    barcode = request.GET.get('barcode')
    detalleVenta = DetalleVenta.objects.all().last()
    articulo = Articulo.objects.get(codigoBarras=barcode)

    articulos = Venta.objects.filter(folio=detalleVenta.pk)
    cont = 0
    total = 0
    for v in articulos:
        if cont > 0:
            total = total + int(v.articulo.precio)
        cont = cont+1
    newVenta = Venta(cantidad=1, precio=articulo.precio, articulo=articulo, folio=detalleVenta)

    try:
        newVenta.save()
        data = {"error": 0, "total":total}
    except ValueError:
        data = {"error":1, "message":"Ocurrio un error"}

    return JsonResponse(data)

@login_required
def popOfCart(request, apk):

    return 1

# Hacer distribuida->
@login_required
def finalizarCobro(request):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)

    lastDetalle = DetalleVenta.objects.all().last()
    lastVentas = Venta.objects.filter(folio=lastDetalle.pk)
    total = 0
    listaArticulos = []
    for v in lastVentas:
        print v.precio
        if v.articulo is not None:
            v.articulo.stock = int(v.articulo.stock) -1
            v.articulo.save()
            listaArticulos.append(v.articulo)
        total = total + int(v.precio)
    lastDetalle.precioFinal = total
    lastDetalle.save()

    newDetalleVenta= DetalleVenta(sucursal=empleado.sucursal, empleadoCobro=empleado)
    newDetalleVenta.save()
    newVenta = Venta(folio=newDetalleVenta, precio=0)
    newVenta.save()

    contexto = {"usuario":empleado, "total":total, "articulos":listaArticulos, "sucursal":lastDetalle.sucursal,
                "empleadoCobro":lastDetalle.empleadoCobro, "fecha":lastDetalle.fecha}
    return render(request, 'ticket.html', contexto)


# de prueba
def ticket(request, folio):
    userId = User.objects.get(username=request.user.username)
    empleado = Empleado.objects.get(usuario=userId)
    listaArticulos=[]

    detalle = DetalleVenta.objects.get(pk=folio)
    articulos = Venta.objects.filter(folio=folio)

    for v in articulos:
        listaArticulos.append(v.articulo)
    if len(listaArticulos):
        listaArticulos.pop(0)
    total = detalle.precioFinal
    fecha = detalle.fecha

    contexto = {"usuario": empleado, "total": total,"fecha":fecha, "articulos":listaArticulos}
    return render(request, 'ticket.html', contexto)