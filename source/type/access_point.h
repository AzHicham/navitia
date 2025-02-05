/* Copyright © 2001-2019, Canal TP and/or its affiliates. All rights reserved.

This file is part of Navitia,
    the software to build cool stuff with public transport.

Hope you'll enjoy and contribute to this project,
    powered by Canal TP (www.canaltp.fr).
Help us simplify mobility and open public transport:
    a non ending quest to the responsive locomotion way of traveling!

LICENCE: This program is free software; you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

Stay tuned using
twitter @navitia
channel `#navitia` on riot https://riot.im/app/#/room/#navitia:matrix.org
https://groups.google.com/d/forum/navitia
www.navitia.io
*/

#pragma once

#include "type/type_interfaces.h"
#include "type/geographical_coord.h"

namespace navitia {
namespace type {

const static int ap_default_value = -1;

struct AccessPoint : public Header, Nameable, hasProperties, HasMessages {
    const static Type_e type = Type_e::AccessPoint;

    // parameters
    std::string stop_code = "";
    bool is_entrance = false;
    bool is_exit = false;
    int pathway_mode = ap_default_value;
    int length = ap_default_value;
    int traversal_time = ap_default_value;
    int stair_count = ap_default_value;
    int max_slope = ap_default_value;
    int min_width = ap_default_value;
    std::string signposted_as = "";
    std::string reversed_signposted_as = "";

    GeographicalCoord coord;

    StopArea* parent_station = nullptr;

    template <class Archive>
    void serialize(Archive& ar, const unsigned int);

    AccessPoint() = default;

    bool operator<(const AccessPoint& other) const;
};

}  // namespace type
}  // namespace navitia
