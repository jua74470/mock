"""
Create users/groups in chroot.  Wrapping the useradd/groupadd utilities.
"""

import grp
import pwd
from mockbuild.util import do_with_status


class ShadowUtils:
    """
    Create a group
    """
    def __init__(self, root):
        self.root = root

    @property
    def _chroot_opts(self):
        return ["--prefix", self.root.make_chroot_path()]

    def _execute_command(self, command, can_fail=False):
        with self.root.uid_manager.elevated_privileges():
            # Execute the command _on host_, not in bootstrap (where we're not
            # sure how old shadow-utils are).
            do_with_status(command + self._chroot_opts, raiseExc=not can_fail)

    def delete_user(self, username, can_fail=False):
        """
        Delete user in self.root (/etc/passwd modified)
        """
        command = ["userdel", "-f", username]
        self._execute_command(command, can_fail=can_fail)

    def delete_group(self, groupname, can_fail=False):
        """
        Delete group in self.root (/etc/group modified)
        """
        command = ["groupdel", groupname]
        self._execute_command(command, can_fail=can_fail)

    def create_group(self, groupname, gid=None):
        """
        Create group in self.root (/etc/group modified)
        """
        command = ["groupadd", groupname]
        if gid is not None:
            command += ["-g", str(gid)]
        self._execute_command(command)

    def create_user(self, username, uid=None, gid=None, home=None):
        """
        Create user in self.root (/etc/passwd modified)
        """
        command = ["useradd", username]
        if uid is not None:
            command += ["-o", "-u", str(uid)]
        if gid is not None:
            command += ["-g", str(gid), "-N"]
        if home is not None:
            command += ["-d", str(home)]
        self._execute_command(command)