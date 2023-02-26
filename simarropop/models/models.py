# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import base64
import io
import gzip
from PIL import Image
import webbrowser


class usuario(models.Model):
    _name = 'res.partner'
    _description = 'Usuario'
    _inherit = 'res.partner'    
    
    name = fields.Char(required = True)
    email = fields.Char(required = True)
    contrasenya = fields.Char(required = True)
    monedero = fields.Float(default=0)
    perfil = fields.Image()
    usuario_valoracion = fields.One2many('simarropop.valoracion', 'valoracion_usuario')
    media_valoracion = fields.Float(compute='_get_avgvaloracion', store=True)
    usuario_articulo = fields.One2many('simarropop.articulo', 'user')
    usuario_favortios = fields.Many2many('simarropop.articulo')
    is_user = fields.Boolean(default = True)

    @api.depends('usuario_valoracion.num_estrellas')
    def _get_avgvaloracion(self):
        for u in self:
            valoraciones = u.usuario_valoracion
            total = 0
            num_val = 0
            for usuario_valoracion in valoraciones:
                total += usuario_valoracion.num_estrellas
                num_val += 1
            u.media_valoracion = total / num_val if num_val else 0
    
    @api.constrains('monedero')
    def monedero_check(self):
        if self.monedero < 0:
            raise ValidationError("El monedero no puede ser negativo")
        

class articulo(models.Model):
    _name = 'simarropop.articulo'
    _description = 'el articulo'

    name = fields.Char()
    precio = fields.Float()
    descripcion = fields.Char()
    articulo_categoria = fields.Many2one('simarropop.categoria')
    imagen = fields.One2many('simarropop.foto', 'imagen_articulo')
    tiempo_horas = fields.Float()
    fecha = fields.Datetime(readonly=True, default=fields.Datetime.now)
    imagen_articulo = fields.Image(max_width = 200, max_height = 200, related='imagen.fotoarticulo') 
    user = fields.Many2one('res.partner')

    @api.model
    def update_hour(self):
        self.search([]).add_hour()

    def add_hour(self):
        for art in self:
            hours = art.tiempo_horas + 1

            art.write({
                "tiempo_horas":hours
            })

    def delete_articulo(self):
        self.unlink()
   
class categoria(models.Model):
    _name = 'simarropop.categoria'
    _description = 'las categorias'

    name = fields.Char()
    icono = fields.Image(max_width = 50, max_height = 50)
    categoria_articulo = fields.One2many('simarropop.articulo', 'articulo_categoria')
    
class foto(models.Model):
    _name = 'simarropop.foto'
    _description = 'las fotos'

    fotoarticulo = fields.Image(max_width=150, max_height=150)
    fotourl = fields.Char()
    imagen_articulo = fields.Many2one('simarropop.articulo')

    @api.model
    def create(self, vals):
        # Obtener la URL de la imagen cargada en el campo "fotoarticulo"
        if vals.get('fotoarticulo'):
            url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url += '/web/content/%s/%s' % (self._name, vals['fotoarticulo'])
            vals['fotourl'] = url
            self.fotourl = {'public': True}

        return super(foto, self).create(vals)

    def write(self, vals):
        # Actualizar la URL si se carga una nueva imagen
        if vals.get('fotoarticulo'):
            url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
            url += '/web/content/%s/%s' % (self._name, vals['fotoarticulo'])
            vals['fotourl'] = url

        return super(foto, self).write(vals)
    
    
    def view_image(self):
        webbrowser.open(self.fotourl)

    
class valoracion(models.Model):
    _name = 'simarropop.valoracion'
    _description = 'las valoraciones'

    name = fields.Char()
    descripcion = fields.Char()
    estrellas = fields.Selection([('1', "Horrible"), ('2',"Malo"), ('3', "Regular"),('4', "Bueno"),('5', "Fantastico")])
    num_estrellas = fields.Float(compute='get_estrellas')
    valoracion_usuario = fields.Many2one('res.partner')


    def get_estrellas(self):
        for v in self:
            if v.estrellas=='1':
                v.write({
                    'num_estrellas':1
                })
            if v.estrellas=='2':
                v.write({
                    'num_estrellas':2
                })
            if v.estrellas=='3':
                v.write({
                    'num_estrellas':3
                })
            if v.estrellas=='4':
                v.write({
                    'num_estrellas':4
                })
            if v.estrellas=='5':
                v.write({
                    'num_estrellas':5
                })

class empleado(models.Model):
    _name = 'simarropop.empleado'
    _description = 'Empleados'   
    
    nombre = fields.Char(required = True, default = "usuario")
    dni = fields.Char(required = True)
    email = fields.Char(required = True)
    contra = fields.Char(required = True)

class venta(models.Model):
    _name = 'sale.order'
    _description = 'Ventas'   
    _inherit = 'sale.order'  
    
    cliente = fields.Many2one('res.partner')
    articulo = fields.Many2one('simarropop.articulo')
   
class usuario_wizard(models.TransientModel):
    _name = 'simarropop.usuario_wizard'
    _description = 'Usuario wizard'

    def _get_client(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    usuario = fields.Many2one('res.partner', default=_get_client)
    name = fields.Char(related='usuario.name')
    quantity_articles = fields.Integer(compute = "search_ventas")

    def search_ventas(self):
        for u in self:
            if(len(usuario.usuario_articulo) > 0 ):
                print(usuario.usuario_articulo)
                return len(usuario.usuario_articulo)


    def ventas(self):
        self.name.write({'Articulos del usuario': self.quantity_articles
                         })


class articulo_mod_wizard(models.TransientModel):
    _name = 'simarropop.articulo_mod_wizard'
    _description = 'Articulo mod wizard'

    def _get_articulo(self):
        return self.env['simarropop.articulo'].browse(self._context.get('active_id'))

    artiuclo = fields.Many2one('res.partner', default=_get_articulo)
    name = fields.Char()
    precio = fields.Float()
    descripcion = fields.Char()
    articulo_categoria = fields.Many2one('simarropop.categoria')
    imagen = fields.One2many('simarropop.foto', 'imagen_articulo')

    def save_changes(self):
        self.articulo.write({
            'name':self.name,
            'precio':self.precio,
            'descripcion':self.descripcion,
            'articulo_categoria':self.articulo_categoria,
            'imagen':self.imagen
        })