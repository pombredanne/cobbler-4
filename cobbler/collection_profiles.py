"""
A profile represents a distro paired with a kickstart file.
For instance, FC5 with a kickstart file specifying OpenOffice
might represent a 'desktop' profile.  For Virt, there are many
additional options, with client-side defaults (not kept here).

Copyright 2006, Red Hat, Inc
Michael DeHaan <mdehaan@redhat.com>

This software may be freely redistributed under the terms of the GNU
general public license.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
"""

import item_profile as profile
import utils
import collection
from cexceptions import *
import action_litesync
from utils import _

#--------------------------------------------

class Profiles(collection.Collection):

    def collection_type(self):
        return "profile"

    def factory_produce(self,config,seed_data):
        return profile.Profile(config).from_datastruct(seed_data)

    def remove(self,name,with_delete=True,with_sync=True,with_triggers=True,recursive=False):
        """
        Remove element named 'name' from the collection
        """

        name = name.lower()

        if not recursive:
            for v in self.config.systems():
                if v.profile.lower() == name:
                    raise CX(_("removal would orphan system: %s") % v.name)

        obj = self.find(name=name)
        if obj is not None:
            if recursive:
                kids = obj.get_children()
                for k in kids:
                    if k.COLLECTION_TYPE == "profile":
                        self.config.api.remove_profile(k, recursive=True)
                    else:
                        self.config.api.remove_system(k)
 
            if with_delete:
                if with_triggers: 
                    self._run_triggers(obj, "/var/lib/cobbler/triggers/delete/profile/pre/*")
                if with_sync:
                    lite_sync = action_litesync.BootLiteSync(self.config)
                    lite_sync.remove_single_profile(name)
            del self.listing[name]
            self.config.serialize_delete(self, obj)
            if with_delete:
                self.log_func("deleted profile %s" % name)
                if with_triggers: 
                    self._run_triggers(obj, "/var/lib/cobbler/triggers/delete/profile/post/*")
            return True
        raise CX(_("cannot delete an object that does not exist: %s") % name)

