from jabberbot import *
import logging
from datetime import datetime, timedelta

MSG_CAMP = "{0[1]} is camping {1} since {0[0]}!"
MSG_CAMP_NOT_FOUND = "System {0} is not currently tracked"
MSG_CAMP_LIST = "Camped systems:"
MSG_CAMP_LIST_ITEM = "{1} -- {0[0]} by {0[1]}"
MSG_UNCAMP_ALL = "You're now uncamped!"
MSG_UNCAMP = "System {0} is now uncamped"
MSG_UNCAMP_NOT_FOUND = "System {0} wasn't camped"
MSG_CHECK_FORUMS = "Check the forums!"
MSG_UNKNOWN_COMMAND = "I can't recognize the command {0}"
DATETIME_FORMAT = "%Y.%m.%d %H%M"
DELTA_CHATROOM = "deltasquadron@chat.pleaseignore.com"
DELTABOT_NICK = "deltabot"

class DeltaBot(JabberBot):

    @botcmd
    def camp(self, mess, args):
        """Show a list of camped systems. If followed by the name of a system, add yourself as camper of the system"""
        if len(args) == 0:
            return self.camp_list_str()
        else:
            self.log.debug(mess)
            # if args in self.camp_entries:
            self.camp[args] = (datetime.utcnow(),
                                    mess.getTo().getNode())
            return MSG_CAMP.format(
                format_value_pair(self.camp[args]), args)
            # else:
            #     return MSG_CAMP_NOT_FOUND.format(args)

    @botcmd
    def uncamp(self, mess, args):
        """Remove from the list of camped systems all that you're camping. If followed by the name of a system, removes the system from the list"""
        node = mess.getTo().getNode()
        if len(args) == 0:
            for k, v in self.camp.items():
                if v[1] == node:
                    self.camp.pop(k)
            return MSG_UNCAMP_ALL
        else:
            if args in self.camp:
                self.camp.pop(args)
                return MSG_UNCAMP.format(args)
            else:
                return MSG_UNCAMP_NOT_FOUND.format(args)

    @botcmd
    def foo(self, mess, args):
        return "bar"


    def unknown_command(self, mess, cmd, args):
        if mess.getBody().endswith("?"):
            return MSG_CHECK_FORUMS
        elif cmd.startswith("!"):
            return MSG_UNKNOWN_COMMAND.format(cmd)
        else:
            return ''

    def camp_list_str(self):
        dt = last_downtime()
        for k, v in self.camp.items():
            if v[0] < dt:
                self.camp.pop(k)

        l = sorted(self.camp.items(), key=lambda x: x[1][1], reverse=True)
        return "\n".join([MSG_CAMP_LIST] + [
            MSG_CAMP_LIST_ITEM.format(format_value_pair(value), key)
            for key, value in l])

    def load_camp_list(self, fname):
        # with open(fname) as f:
        #     self.camp_entries = (x.rstrip() for x in f.readlines())
        #     self.camp_entries = [line for line in self.camp_entries if line]
        #     self.log.info(self.camp_entries)
        self.camp = dict()


def last_downtime():
    now = datetime.utcnow()
    today11 = now.replace(hour=11, minute=0, second=0, microsecond=0)
    if now < today11:
        return today11 - timedelta(1)
    else:
        return today11


def format_value_pair(v):
    return (v[0].strftime(DATETIME_FORMAT), v[1])


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print >>sys.stderr, """
        Usage: %s <jid> <password>
        """ % sys.argv[0]

    username, password = sys.argv[1:]
    deltabot = DeltaBot(username, password, command_prefix='!', res="bot", acceptownmsgs=False)
    deltabot.log.setLevel(logging.DEBUG)
    deltabot.log.addHandler(logging.StreamHandler())
    deltabot.load_camp_list('camp_list.txt')
    deltabot.muc_join_room(DELTA_CHATROOM, DELTABOT_NICK)
    deltabot.serve_forever()
