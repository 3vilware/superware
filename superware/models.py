# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Departamento(models.Model):
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class Categoria(models.Model):
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)
    departamento = models.ForeignKey(Departamento)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class Articulo(models.Model):
    nombre = models.CharField(max_length=90)
    categoria = models.ForeignKey(Categoria)
    descripcion = models.TextField()
    stock = models.IntegerField(null=True)
    precio = models.FloatField(null=True)
    codigoBarras = models.CharField(max_length=90, null=True)
    observaciones = models.TextField(default="Ninguna")
    activo = models.BooleanField(default=True)
    foto = models.FileField(null=True)
    #FALTA PONER EL CAMPO DESCUENTO Y ESTRUCTURARLO


class Sucursal(models.Model):
    nombre = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}'.format(self.nombre)



class ArticuloSucursal(models.Model):
    articulo = models.ForeignKey(Articulo)
    sucursal = models.ForeignKey(Sucursal)

    #Mtriz
class StockGeneral(models.Model):
    articulo = models.ForeignKey(Articulo, on_delete=models.CASCADE)
    sucursal = models.ForeignKey(Sucursal)
    stock = models.IntegerField(null=True)

class Puesto(models.Model):
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class EstatusEmpleado(models.Model):
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class MetodoPago(models.Model):
    descripcion = models.CharField(max_length=80)
    activo = models.BooleanField(default=True)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class Empleado(models.Model):
    nombre = models.CharField(max_length=60)
    apellidoP = models.CharField(max_length=60)
    apellidoM = models.CharField(max_length=60)
    puesto = models.ForeignKey(Puesto)
    estatus = models.ForeignKey(EstatusEmpleado)
    sucursal = models.ForeignKey(Sucursal)
    usuario = models.OneToOneField(User)

#informacion de ventas

class DetalleVenta(models.Model):
    empleadoCobro = models.ForeignKey(Empleado)
    precioFinal = models.FloatField(null=True)
    fecha = models.DateTimeField(auto_now=True)
    sucursal = models.ForeignKey(Sucursal)
    metodoPago = models.ForeignKey(MetodoPago, null=True)

class Venta(models.Model):
    articulo = models.ForeignKey(Articulo, null=True)
    cantidad = models.IntegerField(null=True)
    precio = models.FloatField(null=True)
    folio = models.ForeignKey(DetalleVenta, on_delete=models.CASCADE) #indice principal

#Sistema de turnos
class EstatusTurno(models.Model):
    descripcion = models.CharField(max_length=80)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class TipoCaja(models.Model):
    descripcion = models.CharField(max_length=80)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class EstatusCaja(models.Model):
    descripcion = models.CharField(max_length=80)

    def __unicode__(self):
        return '{}'.format(self.descripcion)

class RendimientoCaja(models.Model):
    clientesAtendidos = models.IntegerField()
    fecha = models.DateField(auto_now=True)
    horasActiva = models.FloatField()

class Caja(models.Model):
    numero = models.IntegerField()
    tipo = models.ForeignKey(TipoCaja)
    carritosEnCola = models.IntegerField()
    estatus = models.ForeignKey(EstatusCaja)

    def __unicode__(self):
        return '{}'.format(self.numero)

class Turno(models.Model):
    numero = models.IntegerField()
    #espera estimada se calcula con rendimiento
    caja = models.ForeignKey(Caja)
    numeroArticulos = models.IntegerField()
    estatus = models.ForeignKey(EstatusTurno)
    tiempoEsperaFinal = models.TimeField(null=True)
