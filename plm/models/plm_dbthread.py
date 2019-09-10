# -*- coding: utf-8 -*-
##############################################################################
#
#    OmniaSolutions, ERP-PLM-CAD Open Source Solutions
#    Copyright (C) 2011-2019 https://OmniaSolutions.website
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this prograIf not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from stat import SF_ARCHIVED
'''
Created on Sep 7, 2019

@author: mboscolo
'''
import logging
import datetime
from odoo import models
from odoo import fields
from odoo import api
from odoo import _
from odoo.exceptions import UserError
from datetime import timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT


class PlmDbthread(models.Model):
    _name = "plm.dbthread"

    documement_name_version = fields.Char(string="Document name and version",
                                          readonly=True)
    threadCode = fields.Char("Thread Code assigned automatically",
                             readonly=True)
    done = fields.Boolean("This thread is done ?",
                          readonly=True)
    error_message = fields.Char("Error message",
                                readonly=True)

    @api.model
    def getNewThreadTransaction(self, list_doc):
        """
        Create all the transaction objects
        """
        threadCode = self.env.get('ir.sequence').next_by_code('plm.dbthread.progress')
        for docDict in list_doc[0]:
            key = docDict.get('KEY', False)
            if key:
                self.create({'documement_name_version': key,
                             'threadCode': threadCode})
        return threadCode

    @api.model
    def cleadUpPrevious(self,
                        document_key):
        for plm_dbthread_id in self.search([('id', '<', self.id),
                                            ('documement_name_version', '=', document_key),
                                            ('done', '=', False)]):
            plm_dbthread_id.done = True
            plm_dbthread_id.error_message = "Automatically close from tread %s " % self.dbThread

    @api.model
    def notifieDoneToDbThread(self, clientArgs):
        document_key, dbThread, clientException = clientArgs[0]
        for plm_dbthread_id in self.search([('documement_name_version', '=', document_key),
                                            ('threadCode', '=', dbThread),
                                            ('done', '=', False)]):
            plm_dbthread_id.done = True
            if clientException:
                plm_dbthread_id.error_message = clientException
            self.cleadUpPrevious(document_key)
            return True
        logging.warning("Try to update %s but not found in the db" % clientArgs[0])
        return False

    @api.model
    def freezeDbThread(self, clientArgs):
        dbThread, error = clientArgs[0]
        for plm_dbthread_id in self.search([('threadCode', '=', dbThread),
                                            ('done', '=', False)]):
            plm_dbthread_id.done = True
            plm_dbthread_id.error_message = error
        return True