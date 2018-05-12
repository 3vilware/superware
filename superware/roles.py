from rolepermissions.roles import AbstractUserRole


class Template(AbstractUserRole):
    available_permissions = {
        'cobrar': True,
        'respaldos': True,
        'verInventario':True,
        'inventarioEditarEliminar':True,
    }

class Cajero(AbstractUserRole):
    available_permissions = {
        'cobrar': True,
        'verInventario':True,
    }

class Supervisor(AbstractUserRole):
    available_permissions = {
        'verInventario':True,
        'inventarioEditarEliminar':True,
    }

class Sistemas(AbstractUserRole):
    available_permissions = {
        'respaldos': True,
        'verInventario':True,
        'inventarioEditarEliminar':True,
    }