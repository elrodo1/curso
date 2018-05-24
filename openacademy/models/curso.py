# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from openerp import api, fields, models
from datetime import datetime, timedelta

from openerp.exceptions import UserError, RedirectWarning, ValidationError

class openacademy_course(models.Model):
    _name='openacademy.course'
    
    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        for course in self:
            new_name="copy of %s" % course.name
        courses_dup=self.search([('name','=ilike',new_name + '%')])
        if len(courses_dup) > 0:
            new_name="%s (%s)" % (new_name, len(courses_dup) + 1)
        default['name']=new_name
        return super(openacademy_course, self).copy(default)
    
    name = fields.Char('Nombre', required=True)
    description = fields.Text('Descripcion')
    responsible_id = fields.Many2one('res.partner', 'Responsable')
    session_ids = fields.One2many('openacademy.session','course_id','Sesiones')
    
    _sql_constraints=[('name_unique','UNIQUE (name)','El nombre debe ser unico'),
        ('name_description_check','CHECK (name <> description)','El nombre y la descripcion deben  ser diferentes'),]

class opeanacademy_session(models.Model):
    _name='openacademy.session'
    
    
    @api.one
    def _take_seats_percent(self):
        for session in self:
            try:
                self.taken_seats_percent=(100 * len(self.attendee_ids)) / self.seats
            except ZeroDivisionError:
                self.taken_seats_percent=0.0
            
    @api.depends('start_date','duration')
    def _determin_end_date(self):
        for session in self:
            if session.start_date and session.duration:
                start_date=datetime.strptime(session.start_date, "%Y-%m-%d")
                duration=timedelta(days=session.duration-1)
                end_date=start_date+duration
                session.end_date=end_date.strftime("%Y-%m-%d")
            else:
                session.end_date=session.start_date
                
    def _set_end_date(self):
        for session in self:
            if session.start_date and session.end_date:
                start_date=datetime.strptime(session.start_date, "%Y-%m-%d")
                end_date=datetime.strptime(session.end_date, "%Y-%m-%d")
                duration=end_date-start_date
                session.duration=duration.days+1
            
    @api.multi
    def action_draft(self):
        return self.write({'state':'draft'})
        
    @api.multi
    def action_cancel(self):
        return self.write({'state':'cancel'})
    @api.multi
    def action_confirm(self):
        return self.write({'state':'confirm'})
        
    @api.multi
    def action_done(self):
        return self.write({'state':'done'})
        
        
    @api.constrains('instructor_id','attendee_ids')
    @api.one
    def _check_instructor_not_attendees(self):
        for session in self:
            lista_attendee=[]
            for attendee in session.attendee_ids:
                lista_attendee.append(attendee.partner_id.id)
            if session.instructor_id and session.instructor_id.id in lista_attendee:
                raise ValidationError(('El instructor no puede ser asistente.'))
            return True
    
    name = fields.Char('Nombre', required=True)
    start_date = fields.Date('Fecha Inicio')
    duration = fields.Integer('Duracion')
    seats = fields.Integer('Num Asientos')
    instructor_id = fields.Many2one('res.partner', 'Instructor', domain=['|',('instructor','=',True), ('category_id.name','ilike','Profesor')])
    course_id = fields.Many2one('openacademy.course', 'Curso', ondelete='cascade')
    attendee_ids = fields.One2many('openacademy.attendee', 'session_id', 'Asistentes')
    taken_seats_percent = fields.Float(string='Porcentaje Asistencia', compute='_take_seats_percent')
    end_date = fields.Date(string='Fecha final', compute='_determin_end_date', inverse='_set_end_date')
    state = fields.Selection([('draft','Borrador'),('confirm','Confirmado'),('done','Listo'),('cancel','Cancelado')], string="Estado", default='draft')
    
    _constraints=[(_check_instructor_not_attendees, "El instructor no puede ser asistente", ['instructor_id','attendee_ids'])]


class openacademy_attendee(models.Model):
    _name='openacademy.attendee'
    
    _rec_name='partner_id'
    
    partner_id = fields.Many2one('res.partner', 'Asistente', ondelete='cascade')
    session_id = fields.Many2one('openacademy.session', 'Sesion', ondelete='cascade')
