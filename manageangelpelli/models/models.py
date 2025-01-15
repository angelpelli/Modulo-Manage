# -*- coding: utf-8 -*-

import datetime
from odoo import models, fields, api

class task(models.Model):
    _name = 'manageangelpelli.task'
    _description = 'manageangelpelli.task'

    name=fields.Char(string="Nombre", readonly= False, required=True, help="Introduzca el nombre")
    description=fields.Text(string="Descripción")
    start_date = fields.Datetime(string="Fecha de inicio")
    end_date = fields.Datetime(string="Fecha de fin")
    is_paused = fields.Boolean(string="¿Esta pausado?")

    sprint=fields.Many2one("manageangelpelli.sprint", compute= "_get_sprint", string="Sprint", store=True)
    technology=fields.Many2many(comodel_name="manageangelpelli.technology", relation="technology_task", column1="tecnologia_id", column2="tarea_id")
    history=fields.Many2one("manageangelpelli.history", string="Historia")

    project=fields.Many2one('manage.project', related='history.project', readonly=True)
    code=fields.Char(compute="_get_code")

    @api.depends('code')
    def _get_sprint(self):
        for task in self:
            sprints = self.env['manageangelpelli.sprint'].search([('project.id', '=', task.history.project.id)])
            found=False
            for sprint in sprints:
                if isinstance(sprint.end_date, datetime.datetime) and sprint.end_date > datetime.datetime.now():
                    task.sprint = sprint.id
                    found=True
            if not found:
                task.sprint = False

    def _get_definition_date(self):
        return datetime.datetime.now()
    
    definition_date = fields.Datetime (default=_get_definition_date)
    

class sprint(models.Model):
    _name = 'manageangelpelli.sprint'
    _description = 'manageangelpelli.sprint'

    name=fields.Char(string="Nombre", readonly= False, required=True, help="Introduzca el nombre")
    description=fields.Text(string="Descripción")
    duration=fields.Integer(default =15)
    start_date = fields.Datetime()
    end_date = fields.Datetime(compute="_get_end_date", store=True)

    project=fields.Many2one("manageangelpelli.project", compute= "_get_project", string="Proyecto")
    task= fields.One2many(string="tareas", comodel_name="manageangelpelli.task", inverse_name='sprint')

    @api.depends('start_date', 'duration')
    def _get_end_date(self):
        for sprint in self:
        #try:
            if isinstance(sprint.start_date, datetime.datetime) and sprint.duration > 0: sprint.end_date = sprint.start_date + datetime.timedelta(days=sprint.duration)
            else:
                sprint.end_date = sprint.start_date
    


class project(models.Model):
    _name = 'manageangelpelli.project'
    _description = 'manageangelpelli.project'

    name=fields.Char(string="Nombre", readonly= False, required=True, help="Introduzca el nombre")
    description=fields.Text(string="Descripción")

    sprint= fields.One2many(string="Sprint", comodel_name="manageangelpelli.sprint", inverse_name='project')
    history= fields.One2many(string="Historia", comodel_name="manageangelpelli.history", inverse_name='project')



class history(models.Model):
    _name = 'manageangelpelli.history'
    _description = 'manageangelpelli.history'

    name=fields.Char(string="Nombre", readonly= False, required=True, help="Introduzca el nombre")
    description=fields.Text(string="Descripción")

    project=fields.Many2one ("manageangelpelli.project",string="Proyecto",required=True, ondelete="cascade")
    task= fields.One2many(string="tareas", comodel_name="manageangelpelli.task", inverse_name='history')
    used_technologies = fields.Many2many ("manageangelpelli.technology", compute="_get_used_technologies")

    def _get_used_technologies(self):
        for history in self:
            technologies=None # Array para concatenar todas las tecnologias. Inicialmente no tiene valor
            for task in history.tasks: # Para cada una de las tareas de la historia
                if not technologies:
                    technologies=task.technologies
                else:
                    technologies=technologies + task.technologies
            history.used_technologies=technologies #Asignar las tecnologías a la historia


class technology(models.Model):
    _name = 'manageangelpelli.technology'
    _description = 'manageangelpelli.technology'

    name=fields.Char(string="Nombre", readonly= False, required=True, help="Introduzca el nombre")
    description=fields.Text(string="Descripción")
    image = fields.Image(string="Imagen")

    task=fields.Many2many(comodel_name = "manageangelpelli.task", relation = "technology_task", column1 = "tarea_id", column2 = "tecnologia_id")




