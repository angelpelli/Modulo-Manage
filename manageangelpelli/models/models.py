# -*- coding: utf-8-*-

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

    definition_date = fields. Datetime(default=lambda p: datetime.datetime.now())

    sprint=fields.Many2one("manageangelpelli.sprint", compute= "_get_sprint", string="Sprint", store=True)
    technology=fields.Many2many(comodel_name="manageangelpelli.technology", relation="technology_task", column1="tecnologia_id", column2="tarea_id")
    history=fields.Many2one("manageangelpelli.history", string="Historia")
    project=fields.Many2one('manageangelpelli.project', related='history.project', readonly=True)

    document_ids = fields.One2many('manageangelpelli.document', 'task_id', string="Documentos")

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
        

class sprint(models.Model):
    _name = 'manageangelpelli.sprint'
    _description = 'manageangelpelli.sprint'

    name=fields.Char(string="Nombre", readonly= False, required=True, help="Introduzca el nombre")
    description=fields.Text(string="Descripción")
    duration=fields.Integer(default =15)
    start_date = fields.Datetime()
    end_date = fields.Datetime(compute="_get_end_date", store=True)

    project=fields.Many2one("manageangelpelli.project", compute= "_get_project", string="Proyecto")
    task=fields.One2many(string="tareas", comodel_name="manageangelpelli.task", inverse_name='sprint')

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

    integration_ids = fields.One2many('manageangelpelli.integration', 'project_id', string="Integraciones")
    document_ids = fields.One2many('manageangelpelli.document', 'project_id', string="Documentos")
    report_ids = fields.One2many('manageangelpelli.report', 'project_id', string="Reportes")


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



class developer (models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'

    is_dev = fields.Boolean(default=True)

    technologies = fields.Many2many('manageangelpelli.technology',
                                    relation='developer_technologies',
                                    column1='developer_id',
                                    column2='technologies_id')


#Nuevo modelo para registrar el tiempo dedicado a cada tarea.
class TimeTracking(models.Model):
    _name = 'manageangelpelli.time_tracking'
    _description = 'Time Tracking'

    task_id = fields.Many2one('manageangelpelli.task', string="Tarea", required=True)
    developer_id = fields.Many2one('res.partner', string="Desarrollador", required=True)
    start_time = fields.Datetime(string="Hora de inicio", required=True)
    end_time = fields.Datetime(string="Hora de fin", required=True)
    duration = fields.Float(string="Duración (horas)", compute="_compute_duration", store=True)

    @api.depends('start_time', 'end_time')
    def _compute_duration(self):
        for record in self:
            if record.start_time and record.end_time:
                delta = record.end_time - record.start_time
                record.duration = delta.total_seconds() / 3600  # Convertir a horas
            else:
                record.duration = 0

#Nuevo modelo para egistrar la asistencia de los desarrolladores a reuniones o sprints.
class Attendance(models.Model):
    _name = 'manageangelpelli.attendance'
    _description = 'Asistencia'

    developer_id = fields.Many2one('res.partner', string="Desarrollador", required=True)
    date = fields.Date(string="Fecha", default=fields.Date.today(), required=True)
    status = fields.Selection([
        ('present', 'Presente'),
        ('absent', 'Ausente'),
        ('late', 'Tarde'),
    ], string="Estado", required=True)


#Modelo para gestionar las integraciones con herramientas externas.
#Implementa métodos para sincronizar datos con herramientas como GitHub, Jira o Slack.
class Integration(models.Model):
    _name = 'manageangelpelli.integration'
    _description = 'Integración con Herramientas Externas'

    name = fields.Char(string="Nombre", required=True)
    tool = fields.Selection([
        ('github', 'GitHub'),
        ('jira', 'Jira'),
        ('slack', 'Slack'),
    ], string="Herramienta", required=True)
    api_key = fields.Char(string="API Key", required=True)
    project_id = fields.Many2one('manageangelpelli.project', string="Proyecto", required=True)

    def sync_tasks_with_jira(self):
        # Lógica para sincronizar tareas con Jira
        pass

    def send_slack_notification(self, message):
        # Lógica para enviar notificaciones a Slack
        pass

#Nuevo modelo para gestionar la documentación relacionada con proyectos, tareas y tecnologías.
class Document(models.Model):
    _name = 'manageangelpelli.document'
    _description = 'Documentación'

    name = fields.Char(string="Nombre", required=True)
    description = fields.Text(string="Descripción")
    file = fields.Binary(string="Archivo", required=True)
    task_id = fields.Many2one('manageangelpelli.task', string="Tarea")
    project_id = fields.Many2one('manageangelpelli.project', string="Proyecto")

#nuevo modelo para generar reportes sobre el progreso de los proyectos y el rendimiento de los desarrolladores.
class Report(models.Model):
    _name = 'manageangelpelli.report'
    _description = 'Reportes'

    name = fields.Char(string="Nombre del Reporte", required=True)
    project_id = fields.Many2one('manageangelpelli.project', string="Proyecto")
    developer_id = fields.Many2one('res.partner', string="Desarrollador")
    report_date = fields.Date(string="Fecha", default=fields.Date.today())
    content = fields.Text(string="Contenido del Reporte")

    def generate_report(self):
        for report in self:
            project = report.project_id
            developer = report.developer_id

            # Obtener datos del proyecto
            total_tasks = len(project.task_ids)
            completed_tasks = len(project.task_ids.filtered(lambda t: t.end_date))
            pending_tasks = total_tasks - completed_tasks

            # Obtener tiempo estimado y real dedicado al proyecto
            estimated_time = sum(task.duration for task in project.task_ids if task.duration)
            actual_time = sum(tracking.duration for task in project.task_ids for tracking in task.time_tracking_ids)

            # Obtener datos del desarrollador (si se especifica)
            developer_data = ""
            if developer:
                developer_tasks = project.task_ids.filtered(lambda t: t.developer_id == developer)
                developer_time = sum(tracking.duration for task in developer_tasks for tracking in task.time_tracking_ids)
                developer_completed_tasks = len(developer_tasks.filtered(lambda t: t.end_date))
                developer_attendance = self.env['manageangelpelli.attendance'].search_count([
                    ('developer_id', '=', developer.id),
                    ('status', '=', 'present')
                ])

                developer_data = f"""
                **Desarrollador: {developer.name}**
                - Tareas completadas: {developer_completed_tasks}
                - Tiempo dedicado: {developer_time} horas
                - Días de asistencia: {developer_attendance}
                """

            # Generar el contenido del reporte
            report.content = f"""
            **Reporte del Proyecto: {project.name}**
            - Fecha del reporte: {report.report_date}
            - Estado del proyecto: {'Completado' if project.end_date else 'En progreso'}
            - Tareas totales: {total_tasks}
            - Tareas completadas: {completed_tasks}
            - Tareas pendientes: {pending_tasks}
            - Tiempo estimado: {estimated_time} horas
            - Tiempo real dedicado: {actual_time} horas

            {developer_data}
            """