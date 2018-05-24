# -*- coding: utf-8 -*-
from django import forms

from superware.models import *


class ArticuloForm(forms.ModelForm):

    class Meta():
        model = Articulo
        fields = ('nombre',
                  'categoria',
                  'descripcion',
                  'stock',
                  'precio',
                  'codigoBarras',
                  'observaciones',
                  'foto')

        widgets = {
            'nombre': forms.TextInput(attrs={'class': 'form-control'}),
            'categoria': forms.Select(attrs={'class': 'form-control'}),
            'descripcion': forms.TextInput(attrs={'class': 'form-control'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control'}),
            'precio': forms.NumberInput(attrs={'class': 'form-control'}),
            'codigoBarras': forms.TextInput(attrs={'class': 'form-control'}),
            'observaciones': forms.TextInput(attrs={'class': 'form-control'}),
        }