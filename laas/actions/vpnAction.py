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

import ldap
import os
import random
from base64 import b64encode
from st2actions.runners.pythonrunner import Action

names = [
    'frodo_baggins', 'samwise_gamgee', 'peregrin_took', 'meriadoc_brandybuck',
    'bilbo_baggins', 'gandalf_grey', 'aragorn_dunadan', 'arwen_evenstar',
    'saruman_white', 'pippin_took', 'merry _randybuck', 'legolas_greenleaf',
    'gimli_gloin', 'anakin_skywalker', 'padme_amidala', 'han_solo',
    'jabba_hut', 'mace_windu', 'count_dooku', 'qui-gon_jinn',
    'admiral_ackbar', 'emperor_palpatine'
]


class VPNAction(Action):
    """
    This class communicates with the ldap server to manage vpn users.
    This class extends the above ABC, and implements the makeNewUser,
    removeOldUser, and __init__ abstract functions you must override to
    extend the VPN_BaseClass
    """

    def __init__(self, config=None):
        """
        init takes the parsed vpn config file as an arguement.
        automatically connects and authenticates on the ldap server
        based on the configuration file
        """
        self.config = config['vpn']
        server = self.config['server']
        self.uri = "ldap://"+server

        self.conn = None
        user = self.config['authentication']['user']
        pswd = self.config['authentication']['pass']
        if os.path.isfile(pswd):
            pswd = open(pswd).read()
        self.connect(user, pswd)

    def connect(self, root_dn, root_pass):
        """
        Opens a connection to the server in the config file
        and authenticates as the given user
        """
        self.conn = ldap.initialize(self.uri)
        self.conn.simple_bind_s(root_dn, root_pass)

    def addUser(self, full_name, passwd):
        """
        Adds a user to the ldap server. Creates the new user with the classes
        and in the directory given in the config file.
        full_name should be two tokens seperated by a space. The first token
        will become the username
        private helper function for the makeNewUser()
        """
        full_name = str(full_name)
        passwd = str(passwd)  # avoids unicode bug
        first = full_name.split('_')[0]
        last = full_name.split('_')[1]
        user_dir = self.config['directory']['user']
        user_dir += ','+self.config['directory']['root']
        user_dir = str(user_dir)
        dn = "uid=" + first + ',' + user_dir
        record = [
                ('objectclass', ['top', 'inetOrgPerson']),
                ('uid', first),
                ('cn', full_name),
                ('sn', last),
                ('userpassword', passwd),
                ('ou', str(self.config['directory']['user'].split('=')[1]))
                ]
        self.conn.add_s(dn, record)
        return first, dn

    def makeNewUser(self, name=None, passwd=None):
        """
        creates a new user in the ldap database, with the given name
        if supplied. If no name is given, we will try to select from the
        pre-written list above, and will resort to generating a random string
        as a username if the preconfigured names are all taken.
        Returns the username and password the user needs to authenticate, and
        the dn that we can use to manage the user.
        """
        if name is None:
            i = 0
            while not self.checkName(name):
                i += 1
                if i == 20:
                    name = self.randoString(8)
                    name += ' '+self.randoString(8)
                    break  # generates a random name to prevent infinite loop
                name = self.genUserName()
        if passwd is None:
            passwd = self.randoString(15)
        username, dn = self.addUser(name, passwd)
        return username, passwd, dn

    def checkName(self, name):
        """
        returns true if the name is available
        """
        if name is None:
            return False
        uid = name.split('_')[0]
        base = self.config['directory']['user'] + ','
        base += self.config['directory']['root']
        filtr = '(uid=' + uid + ')'
        timeout = 5
        ans = self.conn.search_st(
                base,
                ldap.SCOPE_SUBTREE,
                filtr,
                timeout=timeout
                )
        return len(ans) < 1

    @staticmethod
    def randoString(n):
        """
        uses /dev/urandom to generate a random string of length n
        """
        n = int(n)
        # defines valid characters
        alpha = 'abcdefghijklmnopqrstuvwxyz'
        alpha_num = alpha
        alpha_num += alpha.upper()
        alpha_num += "0123456789"

        # generates random string from /dev/urandom
        rnd = b64encode(os.urandom(3*n)).decode('utf-8')
        random_string = ''
        for char in rnd:
            if char in alpha_num:
                random_string += char
        return str(random_string[:n])

    def genUserName(self):
        """
        grabs a random name from the list above
        """
        i = random.randint(0, len(names) - 1)
        return names[i]

    def deleteUser(self, dn):
        dn = str(dn)  # avoids unicode bug
        self.conn.delete(dn)

    def getAllUsers(self):
        """
        returns all the user dn's in the ldap database in a list
        """
        base = self.config['directory']['user'] + ','
        base += self.config['directory']['root']
        filtr = '(objectclass='+self.config['user']['objects'][-1]+')'
        timeout = 10
        ans = self.conn.search_st(
                base,
                ldap.SCOPE_SUBTREE,
                filtr,
                timeout=timeout
                )
        users = []
        for user in ans:
            users.append(user[0])  # adds the dn of each user
        return users
