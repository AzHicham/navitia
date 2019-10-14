# Copyright (c) 2001-2014, Canal TP and/or its affiliates. All rights reserved.
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
# IRC #navitia on freenode
# https://groups.google.com/d/forum/navitia
# www.navitia.io

from jormungandr.instance import Instance
from jormungandr.interfaces.v1 import add_common_status
from jormungandr.street_network.kraken import Kraken
from jormungandr.equipments import EquipmentProviderManager

from collections import OrderedDict

krakenBss = Kraken(instance=None, service_url=None, id="krakenBss", modes=["bss"])
krakenAll = Kraken(instance=None, service_url=None, id="krakenAll", modes=["walking", "bike", "car"])
expected_streetnetworks_status = [
    {'modes': ['walking', 'bike', 'car'], 'id': 'krakenAll', 'class': 'Kraken'},
    {'modes': ['bss'], 'id': 'krakenBss', 'class': 'Kraken'},
]

instant_system_ridesharing_config = [
    {
        "args": {
            "rating_scale_min": 0,
            "crowfly_radius": 500,
            "network": "Network 1",
            "feed_publisher": {
                "url": "https://url_for_publisher",
                "id": "publisher id",
                "license": "Private",
                "name": "Feed publisher name",
            },
            "service_url": "https://service_url",
            "api_key": "private_key",
            "rating_scale_max": 5,
        },
        "class": "jormungandr.scenarios.ridesharing.instant_system.InstantSystem",
    }
]
expected_ridesharing_status = [
    {
        "circuit_breaker": {"current_state": "closed", "fail_counter": 0, "reset_timeout": 60},
        "class": "InstantSystem",
        "crowfly_radius": 500,
        "id": "Instant System",
        "network": "Network 1",
        "rating_scale_max": 5,
        "rating_scale_min": 0,
    }
]

sytral_equipment_details_config = [
    {
        "class": "jormungandr.equipments.sytral.SytralProvider",
        "key": "sytral",
        "args": {
            "url": "https://url_for_equipment_details",
            "fail_max": 5,
            "codes_types": ["TCL_ESCALIER", "TCL_ASCENSEUR"],
            "timeout": 1,
        },
    }
]
expected_equipment_providers_keys = ['sytral']
expected_equipment_providers = [
    {"codes_types": ["TCL_ESCALIER", "TCL_ASCENSEUR"], "fail_max": 5, "key": "sytral", "timeout": 1}
]

# The only purpose of this class is to override get_all_street_networks()
# To bypass the app.config[str('DISABLE_DATABASE')] and the get_models()
# Of the real implementation
class FakeInstance(Instance):
    def __init__(
        self,
        disable_database,
        ridesharing_configurations=None,
        equipment_details_config=None,
        instance_equipment_providers=None,
    ):
        super(FakeInstance, self).__init__(
            context=None,
            name="instance",
            zmq_socket=None,
            street_network_configurations=[],
            ridesharing_configurations=ridesharing_configurations,
            instance_equipment_providers=[],
            realtime_proxies_configuration=[],
            zmq_socket_type=None,
            autocomplete_type='kraken',
            streetnetwork_backend_manager=None,
        )
        self.disable_database = disable_database
        self.equipment_provider_manager = EquipmentProviderManager(equipment_details_config)
        self.equipment_provider_manager.init_providers(instance_equipment_providers)

    def get_models(self):
        return None

    def get_all_street_networks(self):
        return (
            self.get_all_street_networks_json() if self.disable_database else self.get_all_street_networks_db()
        )

    # returns a list
    def get_all_street_networks_json(self):
        return [krakenBss, krakenAll]

    # returns a dict
    def get_all_street_networks_db(self):
        return {krakenBss: ["bss"], krakenAll: ["walking", "bike", "car"]}


def add_common_status_test():
    # get_all_street_networks_json is called
    response1 = call_add_common_status(True)

    # get_all_street_networks_db is called
    response2 = call_add_common_status(False)

    # That's the real purpose of the test
    # The responses must be the same whether we call
    # get_all_street_networks_json or get_all_street_networks_db
    assert response1 == response2


def call_add_common_status(disable_database):
    instance = FakeInstance(
        disable_database,
        ridesharing_configurations=instant_system_ridesharing_config,
        equipment_details_config=sytral_equipment_details_config,
        instance_equipment_providers=["sytral"],
    )
    response = {}
    response['status'] = {}
    add_common_status(response, instance)

    assert response['status']["is_open_data"] == False
    assert response['status']["is_open_service"] == False
    assert response['status']['realtime_proxies'] == []

    # We sort this list because the order is not important
    # And it is easier to compare
    streetnetworks_status = response['status']["street_networks"]
    streetnetworks_status.sort()
    assert streetnetworks_status == expected_streetnetworks_status

    ridesharing_status = response['status']["ridesharing_services"]
    ridesharing_status.sort()
    assert ridesharing_status == expected_ridesharing_status

    equipment_providers_keys = response['status']["equipment_providers_services"]['equipment_providers_keys']
    assert equipment_providers_keys == expected_equipment_providers_keys
    equipment_providers = response['status']["equipment_providers_services"]['equipment_providers']
    equipment_providers.sort()
    assert equipment_providers == expected_equipment_providers

    assert response['status']['autocomplete'] == {'class': 'Kraken'}

    # We sort the response because the order is not important
    # And it is easier to compare
    return OrderedDict(response)
