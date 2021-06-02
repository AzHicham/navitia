# encoding: utf-8

#  Copyright (c) 2001-2014, Canal TP and/or its affiliates. All rights reserved.
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


import math

N_DEG_TO_RAD = 0.01745329238
EARTH_RADIUS_IN_METERS = 6372797.560856


def crowfly_distance_between(start_coord, end_coord):
    lon_arc = (start_coord.lon - end_coord.lon) * N_DEG_TO_RAD
    lon_h = math.sin(lon_arc * 0.5)
    lon_h *= lon_h
    lat_arc = (start_coord.lat - end_coord.lat) * N_DEG_TO_RAD
    lat_h = math.sin(lat_arc * 0.5)
    lat_h *= lat_h
    tmp = math.cos(start_coord.lat * N_DEG_TO_RAD) * math.cos(end_coord.lat * N_DEG_TO_RAD)
    return EARTH_RADIUS_IN_METERS * 2.0 * math.asin(math.sqrt(lat_h + tmp * lon_h))


def get_manhattan_duration(distance, speed):
    return int((distance * math.sqrt(2)) / speed)


def make_speed_switcher(req):
    from jormungandr.fallback_modes import FallbackModes

    return {
        FallbackModes.walking.name: req['walking_speed'],
        FallbackModes.bike.name: req['bike_speed'],
        FallbackModes.car.name: req['car_speed'],
        FallbackModes.car_no_park.name: req['car_no_park_speed'],
        FallbackModes.bss.name: req['bss_speed'],
        FallbackModes.ridesharing.name: req['car_no_park_speed'],
        FallbackModes.taxi.name: req['taxi_speed'],
    }


PARK_RIDE_VALUES = {'yes'}


def pick_up_park_ride_car_park(pt_objects):
    from navitiacommon import type_pb2
    from jormungandr import utils

    def is_poi(pt_object):
        return pt_object.embedded_type == type_pb2.POI

    def is_park_ride(pt_object):
        return any(
            prop.type == 'park_ride' and prop.value.lower() in PARK_RIDE_VALUES
            for prop in pt_object.poi.properties
        )

    park_ride_poi_filter = utils.ComposedFilter().add_filter(is_poi).add_filter(is_park_ride).compose_filters()

    return list(park_ride_poi_filter(pt_objects))
