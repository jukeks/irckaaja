from typing import List


class IrcChannel:
    """
    Channel datastructure. Keeps track of users.
    """

    def __init__(self, name: str, userlist: List[str]) -> None:
        self.name = name
        self.userlist = userlist
        self.userlist_complete = True
        self.topic = ""

    def users_message(self, userlist: List[str]) -> None:
        """
        Usually received on join. Count of these
        messages depend on user count on the channel.
        """
        if self.userlist_complete:
            self.userlist = userlist
            self.userlist_complete = False
        else:
            self.userlist += userlist

    def users_message_end(self) -> None:
        """
        When received, states that all users on channel
        have been listed and userlist is therefore complete.
        """
        self.userlist_complete = True

    def remove_user(self, nick: str) -> None:
        """
        Tries to remove a user from the channel.
        """
        try:
            self.userlist.remove(nick)
        except ValueError:
            pass

    def add_user(self, nick: str) -> None:
        """
        Adds user to channel if not already added.
        """
        if nick not in self.userlist:
            self.userlist.append(nick)
