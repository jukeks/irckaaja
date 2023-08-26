from irckaaja.channel import IrcChannel


def test_channel() -> None:
    c = IrcChannel("#test", ["mathew", "tephew"])

    c.users_message(["a", "b"])
    c.users_message(["c", "d"])
    c.users_message_end()

    assert c.userlist == ["a", "b", "c", "d"]

    c.add_user("e")
    assert "e" in c.userlist

    c.remove_user("a")
    assert "a" not in c.userlist
