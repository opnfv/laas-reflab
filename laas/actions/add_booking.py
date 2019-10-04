##############################################################################
# Copyright 2017 Parker Berberian and Others                                 #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License");            #
# you may not use this file except in compliance with the License.           #
# You may obtain a copy of the License at                                    #
#                                                                            #
#    http://www.apache.org/licenses/LICENSE-2.0                              #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
##############################################################################
import json
import requests
import time
import calendar
from st2actions.runners.pythonrunner import Action


class Add_Booking_Action(Action):

    def run(self, booking_id):
        dashboard = self.action_service.get_value(name="dashboard_url")
        url = dashboard + "api/bookings/" + str(booking_id)
        try:
            booking = requests.get(url).json()
            booking['start'] = self.convert_time(booking['start'])
            booking['end'] = self.convert_time(booking['end'])
            booking['status'] = 1

            # add booking id to bookings list
            bookings = json.loads(
                    self.action_service.get_value(name="bookings", local=False)
                    )
            if booking['id'] in bookings:
                return
            bookings.append(booking['id'])
            self.action_service.set_value(
                    name="bookings",
                    value=json.dumps(bookings),
                    local=False
                    )

            # add booking to datastore
            name = "booking_" + str(booking['id'])
            self.action_service.set_value(
                    name=name,
                    value=json.dumps(booking),
                    local=False
                    )

        except Exception:
            pass

    def convert_time(self, timestr):
        time_struct = time.strptime(timestr, '%Y-%m-%dT%H:%M:%SZ')
        epoch_time = calendar.timegm(time_struct)
        return epoch_time
