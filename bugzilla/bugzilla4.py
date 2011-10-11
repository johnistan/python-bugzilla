# bugzilla4.py - a Python interface to Bugzilla 4.x using xmlrpclib.
#
# Copyright (C) 2011, Andrew Beekhof <andrew@beekhof.net>
# Author: Andrew Beekhof <andrew@beekhof.net>
#
# This program is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; either version 2 of the License, or (at your
# option) any later version.  See http://www.gnu.org/copyleft/gpl.html for
# the full text of the license.

import bugzilla.base
import bugzilla.bugzilla3
import logging

logging.basicConfig()
log = logging.getLogger("bugzilla")

class Bugzilla4(bugzilla.bugzilla3.Bugzilla36):
    '''Concrete implementation of the Bugzilla protocol. This one uses the
    methods provided by standard Bugzilla 4.0.x releases.

    For more info, see:
    http://www.bugzilla.org/docs/4.0/en/html/api/Bugzilla/WebService/Bug.html
    '''

    version = '0.1'
    user_agent = bugzilla.base.user_agent + ' Bugzilla4/%s' % version

    field_aliases = (('short_desc','summary'),
                     ('description','comment'),
                     ('rep_platform','platform'),
                     ('bug_severity','severity'),
                     ('bug_status','status'),
                     ('fixed_in','cf_fixed_in'))

    def _getbugs(self,idlist):
        '''Return a list of dicts of full bug info for each given bug id.
        bug ids that couldn't be found will return None instead of a dict.'''
        idlist = map(lambda i: int(i), idlist)
        r = self._proxy.Bug.get_bugs({'ids':idlist, 'permissive': 1})
        bugdict = dict([(b['id'], b) for b in r['bugs']])
        return [bugdict.get(i) for i in idlist]

    def _query(self,query):
        '''Query bugzilla and return a list of matching bugs.
        For more info, see:
        http://www.bugzilla.org/docs/4.0/en/html/api/Bugzilla/WebService/Bug.html
        '''

        # Can't specify the column list for BZ 4.0
        if query.has_key('column_list'):
            query.pop('column_list')
        return self._proxy.Bug.search(query)

    def _getbugfields(self):
        '''Get the list of valid fields for Bug objects'''
        bug = self._getbug(1)
        keylist = bug.keys()
        if 'assigned_to' not in keylist:
            keylist.append('assigned_to')
        return keylist

    # Adapted from rhbz...

    def _update_bugs(self,ids,updates):
        '''Update the given fields with the given data in one or more bugs.
        ids should be a list of integers or strings, representing bug ids or
        aliases.
        updates is a dict containing pairs like so: {'fieldname':'newvalue'}
        '''
        updates['ids'] = ids
        return self._proxy.Bug.update(updates)

    def _closebug(self,id,resolution,dupeid,fixedin,comment,isprivate,private_in_it,nomail):
        '''Close the given bug. This is the raw call, and no data checking is
        done here. That's up to the closebug method.
        Note that the private_in_it and nomail args are ignored.'''
        update={'bug_status':'RESOLVED','resolution':resolution}
        if dupeid:
            update['resolution'] = 'DUPLICATE'
            update['dupe_id'] = dupeid
        if fixedin:
            update['cf_fixed_in'] = fixedin
        if comment:
            update['comment'] = { 'comment':comment, 'private':isprivate }

        return self._update_bug(id,update)

    def _setstatus(self,id,status,comment='',private=False,private_in_it=False,nomail=False):
        '''Set the status of the bug with the given ID.'''
        update={'bug_status':status}
        if comment:
            update['comment'] = { 'comment':comment, 'private':private }
        return self._update_bug(id,update)