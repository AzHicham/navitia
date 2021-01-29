# Copyright (c) 2001-2019, Canal TP and/or its affiliates. All rights reserved.
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

from __future__ import absolute_import, print_function, unicode_literals, division
from jormungandr import cache, app, new_relic
import pybreaker
import logging
import requests as requests
from six.moves.urllib.parse import urlencode


class ForsetiProvider(object):
    """
    Class managing calls to forseti webservice, providing free_floatings
    """

    def __init__(self, url, timeout=2, **kwargs):
        self.logger = logging.getLogger(__name__)
        self.url = url
        self.timeout = timeout
        self.breaker = pybreaker.CircuitBreaker(
            fail_max=kwargs.get('circuit_breaker_max_fail', app.config['CIRCUIT_BREAKER_MAX_FORSETI_FAIL']),
            reset_timeout=kwargs.get(
                'circuit_breaker_reset_timeout', app.config['CIRCUIT_BREAKER_FORSETI_TIMEOUT_S']
            ),
        )

    @cache.memoize(app.config.get(str('CACHE_CONFIGURATION'), {}).get(str('TIMEOUT_FORSETI'), 30))
    def _call_webservice(self, arguments):
        """
        Call free_floatings webservice with URL defined in settings
        :return: data received from the webservice
        """
        logging.getLogger(__name__).debug('forseti free_floatings service , call url : {}'.format(self.url))
        result = None
        try:
            url = "{}?{}".format(self.url, urlencode(arguments, doseq=True))
            response = self.breaker.call(requests.get, url=url, timeout=self.timeout)
            return response
            self.record_call("OK")
        except pybreaker.CircuitBreakerError as e:
            logging.getLogger(__name__).error('Service SytralRT is dead (error: {})'.format(e))
            self.record_call('failure', reason='circuit breaker open')
        except requests.Timeout as t:
            logging.getLogger(__name__).error('SytralRT service timeout (error: {})'.format(t))
            self.record_call('failure', reason='timeout')
        except Exception as e:
            logging.getLogger(__name__).exception('SytralRT service error: {}'.format(e))
            self.record_call('failure', reason=str(e))
        return result

    def record_call(self, status, **kwargs):
        """
        status can be in: ok, failure
        """
        params = {'free_floatings_id': "Forseti", 'dataset': "?????", 'status': status}
        params.update(kwargs)
        new_relic.record_custom_event('parking_status', params)

    def get_free_floatings(self, arguments):
        """
        Get free-floating information from Forseti webservice
        """
        raw_response = self._call_webservice(arguments)

        # Here process data ??
        if raw_response:
            resp = self.response_marshaler(raw_response)
            return resp
        return None

    @classmethod
    def _check_response(cls, response):
        if response is None:
            raise ForsetiError('impossible to access free-floating service')
        if response.status_code == 503:
            raise ForsetiUnavailable('forseti responded with 503')
        if response.status_code != 200:
            error_msg = 'free-floating request failed with HTTP code {}'.format(response.status_code)
            if response.text:
                error_msg += ' ({})'.format(response.text)
            raise ForsetiError(error_msg)

    @classmethod
    def response_marshaler(cls, response):
        cls._check_response(response)
        try:
            json_response = response.json()
        except ValueError:
            logging.getLogger(__name__).error(
                "impossible to get json for response %s with body: %s", response.status_code, response.text
            )
            raise
        # Clean dict objects depending on depth passed in request parameter.
        # json_response = cls._clean_response(json_response, depth)
        from jormungandr.interfaces.v1.serializer.free_floating import FreeFloatingsSerializer

        resp = FreeFloatingsSerializer(json_response).data
        return resp


class ForsetiError(RuntimeError):
    pass


class ForsetiUnavailable(RuntimeError):
    pass
