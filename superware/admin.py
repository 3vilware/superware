# -*- coding: utf-8 -*-

import inspect
import pyclbr

from django.contrib import admin
from django.db import models

import superware.models as modelos


def registrar_modelos(my_models):
    classes = pyclbr.readmodule_ex(my_models.__name__)
    for model in classes:
        model = getattr(my_models, model)
        if inspect.isclass(model) and issubclass(model, models.Model):
            admin.site.register(model)

registrar_modelos(modelos)


admin.site.site_header = 'Super Admin'
admin.site.site_title = 'SuperWare'