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


import abc
import six

from jormungandr import cache, app, new_relic
import pybreaker
import logging
import requests as requests
from six.moves.urllib.parse import urlencode


class ExternalServiceError(RuntimeError):
    pass


class ExternalServiceUnavailable(RuntimeError):
    pass


@six.add_metaclass(abc.ABCMeta)
class AbstractExternalService(object):
    def _call_webservice(self, arguments):
        """
        Call external_services webservice with URL defined in settings
        :return: data received from the webservice
        """
        logging.getLogger(__name__).debug(f'forseti external_services service , call url : {self.service_url}')
        result = None
        try:
            url = f"{self.service_url}?{urlencode(arguments, doseq=True)}"
            result = self.breaker.call(requests.get, url=url, timeout=self.timeout)
            self.record_call(url=url, status="OK")
        except pybreaker.CircuitBreakerError as e:
            logging.getLogger(__name__).error(f'Service Forseti is dead (error: {e})')
            self.record_call(url=url, status='failure', reason='circuit breaker open')
        except requests.Timeout as t:
            logging.getLogger(__name__).error(f'Forseti service timeout (error: {t})')
            self.record_call(url=url, status='failure', reason='timeout')
        except Exception as e:
            logging.getLogger(__name__).exception(f'Forseti service error: {e}')
            self.record_call(url=url, status='failure', reason=str(e))
        return result

    def record_call(self, url, status, **kwargs):
        """
        status can be in: ok, failure
        """
        params = {'external_service_id': "Forseti", 'status': status, 'external_service_url': url}
        params.update(kwargs)
        new_relic.record_custom_event('external_service_status', params)

    @abc.abstractmethod
    def get_response(self, arguments):
        """
        Get external service information from Forseti webservice
        """
        pass

    @classmethod
    def _check_response(cls, response):
        if not response:
            raise ExternalServiceError('impossible to access external service')
        if response.status_code == 503:
            raise ExternalServiceUnavailable('forseti responded with 503')
        if response.status_code != 200:
            error_msg = f'external service request failed with HTTP code {response.status_code}'
            if response.text:
                error_msg += f' ({response.text})'
            raise ExternalServiceError(error_msg)
