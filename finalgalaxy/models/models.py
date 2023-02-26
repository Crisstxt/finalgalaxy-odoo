# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
import random


class player(models.Model):
    _name = 'res.partner'
    _description = 'Jugador'
    _inherit = 'res.partner'    

    name = fields.Char(required=True)
    password = fields.Char(required=True)
    level = fields.Integer(default=1)
    exp = fields.Integer(default=0)
    planeta = fields.One2many('finalgalaxy.planet', 'player')
    planeta_contador = fields.Integer(compute='_get_total_planets')
    faction_player = fields.Many2one('finalgalaxy.faction')
    battle_points = fields.Integer(default=1000)
    battle_history = fields.Many2many('finalgalaxy.battle', compute="_get_battles")
    is_player = fields.Boolean(default=False) 

    @api.onchange('level','exp')
    def _update_level(self):
        if self.level * 200 == self.exp:
            self.level = self.level + 1
            self.exp = 0

    @api.depends('planeta')
    def _get_total_planets(self):
        for p in self:
            p.planeta_contador = len(p.planeta)

    @api.constrains('level', 'exp')
    def _level_check(self):
        if self.exp < 0 or self.level < 0:
            raise ValidationError("El nivel o el experiencia no puede ser menor que 0")

    def _get_battles(self):
        self.battle_history = self.env['finalgalaxy.battle'].search([('status', '=', 2), '|', ('attack_player', '=', self.id), ('defense_player', '=', self.id)])

   
class planet(models.Model):
    _name = 'finalgalaxy.planet'
    _description = 'Planeta'

    name = fields.Char(required=True)
    credit = fields.Float(default=50.0)
    metal = fields.Float(default=50)
    food = fields.Float(default=100)
    troops = fields.Integer(default=5)
    ships = fields.Integer(default=0)
    population_used = fields.Integer(default=0)
    population_available = fields.Integer(default=15)
    building_planet = fields.One2many('finalgalaxy.building', 'planeta')
    building_available = fields.Many2many('finalgalaxy.building_type', compute='_get_buildings')
    player = fields.Many2one('res.partner', ondelete="cascade", domain=[('is_player', '=', True)], required=True)
    player_image = fields.Image(related='player.faction_player.image')
    faction = fields.Many2one('finalgalaxy.faction', related='player.faction_player')

    def _get_buildings(self):
        self.building_available = self.env['finalgalaxy.building_type'].search([])

    @api.model
    def produce(self):
        self.search([]).produce_recursos()

    def produce_recursos(self):
        for p in self:
            total = self.env['finalgalaxy.building'].search([('build_type', '=', 2), ('planeta.id','=',p.id)])
            if len(total) > 0:
                p.credit = p.credit + 10
                p.food = p.food + 10 * len(total)
                p.metal = p.metal + 10 * len(total)  
            else:
                p.credit = p.credit + 10
    
    def create_troop(self):
        for b in self:
            total = self.env['finalgalaxy.building'].search([('build_type', '=', 1), ('planeta.id','=',b.id)])
        if len(total) > 0:
            if b.credit >= 25 and b.food >= 30 and b.population_used + 2 * len(total) <= b.population_available:
                b.troops = b.troops + 1 * len(total)
                b.population_used = b.population_used  + 2 * len(total)
            else:
                raise ValidationError("Recursos insuficientes o No tienes Espacio en el planeta")                          
        else:
            raise ValidationError("No tienes Cuarteles Para crear Tropas")

    def create_ship(self):
        for b in self:
            total = self.env['finalgalaxy.building'].search([('build_type', '=', 4), ('planeta.id','=',b.id)])
        if len(total) > 0:
            if b.credit >= 45 and b.food >= 10 and b.metal >= 25 and b.population_used + 3 * len(total)  <= b.population_available:
                b.ships = b.ships + 1 * len(total)
                b.population_used = b.population_used + 3 * len(total)
            else:
                raise ValidationError("Recursos insuficientes o No tienes Espacio en el planeta")                          
        else:
            raise ValidationError("No tienes Estacion espacial para crear Naves") 

    def delete_planet(self):
        self.unlink()

class faction(models.Model):
    _name = 'finalgalaxy.faction'
    _description = 'Facciones'

    name = fields.Char(required=True)
    description = fields.Char()
    image = fields.Image(max_height=250,max_width=250)

class building(models.Model):
    _name = 'finalgalaxy.building'
    _description = 'Edificios'

    name = fields.Char()
    image = fields.Image(max_height=250, max_width=250)
    population_add = fields.Integer()
    build_type = fields.Selection([('1','Cuartel'),('2','recursos'),('3','casa'),('4','Estacion Espacial')])
    planeta = fields.Many2one('finalgalaxy.planet', ondelete="cascade")

class building_type(models.Model):
    _name = 'finalgalaxy.building_type'
    _description = 'Tipos de Edificios'

    name = fields.Char(required=True)
    image = fields.Image(max_height=250, max_width=250)
    credit = fields.Float(default=0)
    metal = fields.Float(default=0)
    food = fields.Float(default=0)
    population_add = fields.Integer()
    build_type = fields.Selection([('1','Cuartel'),('2','recursos'),('3','casa'),('4','Estacion Espacial')])

    def build(self):
        for b in self:
            planeta_id = self.env['finalgalaxy.planet'].browse(self.env.context['ctx_planet'])[0]
            if planeta_id.credit >= b.credit and planeta_id.food >= b.food and planeta_id.metal >= b.metal:
                self.env['finalgalaxy.building'].create({
                    "name": b.name,
                    "image": b.image,
                    "population_add": b.population_add,
                    "build_type": b.build_type,
                    "planeta": planeta_id.id
                })
                planeta_id.credit = planeta_id.credit - b.credit
                planeta_id.food = planeta_id.food - b.food
                planeta_id.metal = planeta_id.metal - b.metal
                planeta_id.population_available = planeta_id.population_available + b.population_add
            else:
                raise ValidationError("Recursos insuficientes")


class battle(models.Model):
    _name = 'finalgalaxy.battle'
    _description = 'Batallas'

    name = fields.Char(required=True)
    attack_player = fields.Many2one('res.partner', domain=[('is_player', '=', True)],required=True)
    attack_player_image = fields.Image(related='attack_player.image_1920')
    attack_player_batalla_ganadas = fields.Integer(default=0)
    defense_player = fields.Many2one('res.partner', domain=[('is_player', '=', True)],required=True)
    defense_player_image = fields.Image(related='defense_player.image_1920')
    defense_player_batalla_ganadas = fields.Integer(default=0)
    planet_attack = fields.Many2one('finalgalaxy.planet',required=True)
    planet_defense = fields.Many2one('finalgalaxy.planet',required=True)
    status = fields.Selection([('1','Preparacion'),('2','Finalizado')], default='1')
    winner = fields.Many2one('res.partner')
    date = fields.Datetime(readonly=True, default=fields.Datetime.now)

    @api.onchange('attack_player')
    def onchange_player1(self):
        return {
            'domain': {
                'planet_attack': [('id', 'in', self.attack_player.planeta.ids)],
                'defense_player': [('id', '!=', self.attack_player.id), ('is_player', '=', True)],
                'defense_player.faction_player': [('id','!=', self.attack_player.faction_player.id)],
            }
        }

    @api.onchange('defense_player')  
    def onchange_player2(self):
        return {
            'domain': {
                'planet_defense': [('id', 'in', self.defense_player.planeta.ids)],
                'attack_player': [('id', '!=', self.defense_player.id), ('is_player', '=', True)],
                'attack_player.faction_player': [('id','!=', self.defense_player.faction_player.id)],
            }
        } 

    def start_battle(self):
        for b in self:
            b.search([]).battle_space()
            b.search([]).battle_ground()
       

            if b.attack_player_batalla_ganadas > b.defense_player_batalla_ganadas:
                b.attack_player.exp += 10
                b.attack_player.battle_points += 5
                b.defense_player.exp += 5
                b.defense_player.battle_points += 1
                b.planet_defense.troops -= b.planet_defense.troops
                b.planet_defense.ships -= b.planet_defense.ships
                b.winner = b.attack_player.id
            else:

                b.attack_player.exp += 5
                b.attack_player.battle_points += 1
                b.defense_player.exp += 10
                b.defense_player.battle_points += 5
                b.planet_attack.troops -= b.planet_attack.troops
                b.planet_attack.ships -= b.planet_attack.ships
                b.winner = b.defense_player.id

            if b.attack_player_batalla_ganadas == b.defense_player_batalla_ganadas:            
                resultado = random.randrange(101)
                if resultado <= 25:
                    b.attack_player.exp += 10
                    b.attack_player.battle_points += 5
                    b.defense_player.exp += 5
                    b.defense_player.battle_points += 1
                    b.planet_defense.troops -= b.planet_defense.troops
                    b.planet_defense.ships -= b.planet_defense.ships
                    b.winner = b.attack_player.id
                else:
                    b.attack_player.exp += 5
                    b.attack_player.battle_points += 1
                    b.defense_player.exp += 10
                    b.defense_player.battle_points += 5
                    b.planet_attack.troops -= b.planet_attack.troops
                    b.planet_attack.ships -= b.planet_attack.ships
                    b.winner = b.defense_player.id 
            
        b.status = '2'
              


    def battle_ground(self):
        for b in self:
            total = b.planet_attack.troops + b.planet_defense.troops
            
            batalla_resultado = random.randrange(total+1)

            if batalla_resultado <= b.planet_defense.troops and batalla_resultado > b.planet_attack.troops:
                b.defense_player_batalla_ganadas += 1
            
            if batalla_resultado <= b.planet_attack.troops and batalla_resultado > b.planet_defense.troops:
                b.attack_player_batalla_ganadas += 1


    def battle_space(self):
        for b in self:
            total = b.planet_attack.ships + b.planet_defense.ships
            
            batalla_resultado = random.randrange(total+1)

            if batalla_resultado <= b.planet_defense.ships and batalla_resultado > b.planet_attack.ships:
                b.defense_player_batalla_ganadas += 1
            
            if batalla_resultado <= b.planet_attack.ships and batalla_resultado > b.planet_defense.ships:
                b.attack_player_batalla_ganadas += 1



#-- Wizard Section -- 

class planet_add_wizard(models.TransientModel):
    _name = 'finalgalaxy.planet_add_wizard'
    _description = 'Crear planeta'

    def _get_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    name = fields.Char(required=True)
    player = fields.Many2one('res.partner', default=_get_player) 

    def create_planet(self):
        if self.player.battle_points == 1000:
            values = {
                'name': self.name,
                'player': self.player.id
            }
            self.env['finalgalaxy.planet'].create(values)
            
            self.player.battle_points = 0

            return{'type': 'ir.actions.act_window_close'}
        else:
            raise ValidationError("puntos insuficientes")

class planet_mod_wizard(models.TransientModel):
    _name = 'finalgalaxy.planet_mod_wizard'
    _description = 'Modificar planeta'

    def _get_planet(self):
        return self.env['finalgalaxy.planet'].browse(self._context.get('active_id'))

    planet = fields.Many2one('finalgalaxy.planet', default=_get_planet)
    name = fields.Char(readonly=False)
    credit = fields.Float(readonly=False)
    metal = fields.Float(readonly=False)
    food = fields.Float(readonly=False)
    troops = fields.Integer(readonly=False)
    ships = fields.Integer(readonly=False)
    population_used = fields.Integer(readonly=False)
    population_available = fields.Integer(readonly=False)
        

    def save_changes(self):
        self.planet.write({
            'name': self.name,
            'credit': self.credit,
            'metal': self.metal,
            'food': self.food,
            'troops': self.troops,
            'ships': self.ships,
            'population_used': self.population_used,
            'population_available': self.population_available
        })

class battle_create_wizard(models.TransientModel):
    _name = 'finalgalaxy.battle_create_wizard'
    _description = 'Crear una Batalla'   

    def _get_player(self):
        return self.env['res.partner'].browse(self._context.get('active_id'))

    name = fields.Char(required=True)
    attack_player = fields.Many2one('res.partner', default=_get_player)
    attack_player_image = fields.Image(related='attack_player.image_1920')
    attack_player_batalla_ganadas = fields.Integer(default=0)
    defense_player = fields.Many2one('res.partner', domain=[('is_player', '=', True)])
    defense_player_image = fields.Image(related='defense_player.image_1920')
    defense_player_batalla_ganadas = fields.Integer(default=0)
    planet_attack = fields.Many2one('finalgalaxy.planet',required=True)
    planet_defense = fields.Many2one('finalgalaxy.planet')
    status = fields.Selection([('1','Preparacion'),('2','Finalizado')], default='1')
    winner = fields.Many2one('res.partner')
    date = fields.Datetime(readonly=True, default=fields.Datetime.now)
    state = fields.Selection([('1','attack player'),('2','defense player'),('3','battle')], default='1')

    @api.onchange('attack_player')
    def onchange_player1(self):
        return {
            'domain': {
                'planet_attack': [('id', 'in', self.attack_player.planeta.ids)],
                'defense_player': [('id', '!=', self.attack_player.id), ('is_player', '=', True)],
                'defense_player.faction_player': [('id','!=', self.attack_player.faction_player.id)],
            }
        }

    @api.onchange('defense_player')  
    def onchange_player2(self):
        return {
            'domain': {
                'planet_defense': [('id', 'in', self.defense_player.planeta.ids)],
                'attack_player': [('id', '!=', self.defense_player.id), ('is_player', '=', True)],
                'attack_player.faction_player': [('id','!=', self.defense_player.faction_player.id)],
            }
        } 

    def action_previous(self):
        if self.state == '2':
            self.state = '1'
        elif self.state == '3':
            self.state = '2'
        return{
            'name': 'create battle',
            'type': 'ir.actions.act_window',
            'res_model': 'finalgalaxy.battle_create_wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id
        }
    
    def action_next(self):
        if self.state == '1':
            self.state = '2'
        elif self.state == '2':
            if not self.defense_player or not self.planet_defense:
                 raise ValidationError("No has seleccionado al jugador defensivo o su planeta")
            else:
                self.state = '3'
        return {
            'name': 'create battle',
            'type': 'ir.actions.act_window',
            'res_model': 'finalgalaxy.battle_create_wizard',
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': dict(self._context, attack_player_context=self.attack_player.id)            
        }