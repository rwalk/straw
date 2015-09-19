#!/usr/bin/python3

def quiet_wrap(cmd):
    return(" ".join(["nohup",cmd, "< /dev/null > std.out 2> std.err &"]))
