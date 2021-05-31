# coding: utf-8

# Copyright (c) 2001-2021, Canal TP and/or its affiliates. All rights reserved.
#
# This file is part of Navitia,
#     the software to build cool stuff with public transport.
#
# Hope you'll enjoy and contribute to this project,
#     powered by Canal TP (www.canaltp.fr).
# Help us simplify mobility and open public transport:
#     a non ending quest to the responsive locomotion way of traveling!
#
# LICENCE: This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Stay tuned using
# twitter @navitia
# channel `#navitia` on riot https://riot.im/app/#/room/#navitia:matrix.org
# https://groups.google.com/d/forum/navitia
# www.navitia.io


from flask import request
import flask_restful
from flask_restful import marshal_with, marshal, abort

import sqlalchemy
from tyr.fields import external_service_list_fields, external_service_fields
from tyr.formats import external_service_format
from navitiacommon import models, utils
import logging
from tyr.validations import InputJsonValidator


class ExternalService(flask_restful.Resource):
    @marshal_with(external_service_list_fields)
    def get(self, id=None, version=0):
        if id:
            try:
                return {'external_services': [models.ExternalService.find_by_id(id)]}
            except sqlalchemy.orm.exc.NoResultFound:
                return {'external_services': []}, 404
        else:
            return {'external_services': models.ExternalService.all()}

    @InputJsonValidator(external_service_format)
    def put(self, id=None, version=0):
        """
        Create or update an external service like free_floatings, vehicle_occupancies in db
        """
        input_json = request.get_json(force=True, silent=False)
        try:
            service = models.ExternalService.find_by_id(id)
            status = 200
        except sqlalchemy.orm.exc.NoResultFound:
            logging.getLogger(__name__).info(f"Create a new service {id}")
            service = models.ExternalService(id)
            models.db.session.add(service)
            status = 201
        service.from_json(input_json)
        try:
            models.db.session.commit()
        except sqlalchemy.exc.IntegrityError as ex:
            abort(400, status="error", message=str(ex))
        return {'external_services': [marshal(service, external_service_fields)]}, status

    def delete(self, id=None, version=0):
        """
        Delete an external service in db, i.e. set parameter DISCARDED to TRUE
        """
        if not id:
            abort(400, status="error", message='id is required')
        try:
            provider = models.ExternalService.find_by_id(id)
            provider.discarded = True
            models.db.session.commit()
            return None, 204
        except sqlalchemy.orm.exc.NoResultFound:
            abort(404, status="error", message='object not found')
