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

import requests
import time
import calendar
import json
from st2reactor.sensor.base import PollingSensor


class Pharos_api(PollingSensor):
    """
    This class listens to the dashboard and starts/stops bookings accordingly.
    """

    def getBookingList(self):
        return json.loads(
                self.sensor_service.get_value(name='bookings', local=False)
                )

    def updateBookingList(self, blist):
        self.sensor_service.set_value(
                name='bookings',
                value=json.dumps(blist),
                local=False
                )

    def AddBooking(self, new_booking):
        """
        checks if booking is in the database, and adds it if it isnt
        """
        # first, check if booking is already expired
        if time.time() > new_booking['end']:
            return
        # check if booking already in db
        booking_list = self.getBookingList()
        if new_booking['id'] in booking_list:
            return
        new_booking['status'] = 0  # add status code
        booking_list.append(new_booking['id'])
        name = "booking_" + str(new_booking['id'])
        self.sensor_service.set_value(
                name=name,
                value=json.dumps(new_booking),
                local=False
                )
        self.updateBookingList(booking_list)

    def convertTimes(self, booking):
        """
        this method will take the time reported by Pharos in the
        format yyyy-mm-ddThh:mm:ssZ
        and convert it into seconds since the epoch,
        for easier management
        """
        booking['start'] = self.pharosToEpoch(booking['start'])
        booking['end'] = self.pharosToEpoch(booking['end'])

    def pharosToEpoch(self, timeStr):
        """
        Converts the dates from the dashboard to epoch time.
        """
        time_struct = time.strptime(timeStr, '%Y-%m-%dT%H:%M:%SZ')
        epoch_time = calendar.timegm(time_struct)
        return epoch_time

    def checkBookings(self):
        """
        This method checks all the bookings in our database to see if any
        action is required.
        """

        # get all active bookings from database into a usable form
        booking_list = self.getBookingList()
        for booking_id in booking_list:
            booking = self.getBooking(booking_id)
            # first, check if booking is over
            if time.time() > booking['end']:
                self.log.info("ending the booking with id %i", booking_id)
                self.endBooking(booking)
            # Then check if booking has begun and the host is still idle
            elif time.time() > booking['start'] and booking['status'] < 1:
                self.log.info("starting the booking with id %i", booking['id'])
                self.startBooking(booking)

    def startBooking(self, booking):
        """
        Starts the scheduled booking on the requested host with
        the correct config file.
        The provisioning process gets spun up in a subproccess,
        so the api listener is not interupted.
        """
        host = self.getServer(pharos_id=booking['resource_id'])['hostname']
        self.log.info("Detected a new booking started for host %s", host)
        self.setBookingStatus(booking['id'], 1)  # mark booking started
        # dispatch trigger into system
        trigger = "pharoslaas.start_deployment_trigger"
        payload = {"host": host, "installer": booking['installer_name']}
        payload['scenario'] = booking['scenario_name']
        payload['booking'] = booking['id']
        self.sensor_service.dispatch(trigger=trigger, payload=payload)

    def endBooking(self, booking):
        """
        Resets a host once its booking has ended.
        """
        host = self.getServer(pharos_id=booking['resource_id'])['hostname']
        self.log.info('Lease expired. Resetting host %s', host)
        self.setBookingStatus(booking['id'], 3)
        self.removeBooking(booking['id'])
        # dispatch trigger to clean
        host = self.getServer(pharos_id=booking['resource_id'])['hostname']
        trigger = "pharoslaas.end_deployment_trigger"
        payload = {"host": host, "booking": booking['id']}
        if 'vpn_key' in booking.keys():
            payload['key'] = booking['vpn_key']
        else:
            payload['key'] = ''
        self.sensor_service.dispatch(trigger=trigger, payload=payload)

    def getServer(self, fog_name=None, hostname=None, pharos_id=None):
        key = ""
        value = ""
        if fog_name is not None:
            key = "fog_name"
            value = fog_name
        elif hostname is not None:
            key = "hostname"
            value = hostname
        elif pharos_id is not None:
            key = "pharos_id"
            value = pharos_id
        for server in self.servers:
            if server[key] == value:
                return server

    def getBooking(self, booking_id):
        name = "booking_" + str(booking_id)
        return json.loads(
                self.sensor_service.get_value(
                    name=name,
                    local=False
                    )
                )

    def setBookingStatus(self, booking_id, status):
        booking = self.getBooking(booking_id)
        booking['status'] = status
        name = "booking_" + str(booking_id)
        self.sensor_service.set_value(
                name=name,
                value=json.dumps(booking),
                local=False
                )

    def removeBooking(self, booking_id):
        blist = self.getBookingList()
        blist.remove(booking_id)
        self.updateBookingList(blist)
        name = "booking_" + str(booking_id)
        self.sensor_service.delete_value(name=name, local=False)

    # Sensor Interface Methods #

    def setup(self):
        """
        This method is called by stackstorm once to setup this polling sensor.
        Basically __init__, assigns instance variables, etc
        """
        server_names = json.loads(
                self.sensor_service.get_value('hosts', local=False)
                )
        self.servers = []
        for server in server_names:
            self.servers.append(
                    json.loads(
                        self.sensor_service.get_value(server, local=False)
                        )
                    )
        self.resource_ids = []
        for host in self.servers:
            self.resource_ids.append(host['pharos_id'])
        self.log = self.sensor_service.get_logger(name=self.__class__.__name__)
        self.dashboard = self.sensor_service.get_value(
                name='dashboard_url',
                local=False
                )
        self.log.info("connecting to dashboard at %s", self.dashboard)
        # get token here for when dashboard supports it

    def poll(self):
        """
        this method will continuously poll the pharos dashboard.
        If a booking is found on our server,
        we will start a deployment in the background with the
        proper config file for the requested
        installer and scenario.
        """
        self.log.debug("%s", "Beginning polling of dashboard")
        try:
            url = self.dashboard+"/api/bookings/"
            bookings = requests.get(url).json()
            for booking in bookings:
                if booking['resource_id'] in self.resource_ids:
                    self.convertTimes(booking)
                    self.AddBooking(booking)
            self.checkBookings()
        except Exception:
            self.log.exception('%s', "failed to connect to dashboard")

    def cleanup(self):
        # called when st2 goes down
        pass

    def add_trigger(self, trigger):
        # called when trigger is created
        pass

    def update_trigger(self, trigger):
        # called when trigger is updated
        pass

    def remove_trigger(self, trigger):
        # called when trigger is deleted
        pass
