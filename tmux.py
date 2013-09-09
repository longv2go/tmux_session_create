#!/usr/bin/python 

from json import JSONDecoder, JSONEncoder
from pprint import pprint
import commands
import optparse

_CONF_FILE = './tmux.js'

def jsencode(p):
    return JSONEncoder().encode(p)

def jsdecode(j):
    return JSONDecoder().decode(j)

def parse_args():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)

    parser.add_option("-c", help='The config file', action='store', dest='conf_file')

    options, args = parser.parse_args()
    
    conf_file = options.conf_file or 'tmux.js'
    return conf_file

def _excute_cmd(cmd):
    return commands.getstatusoutput(cmd)

def _session_exist(name):
    cmd = "tmux has-session -t %s" % name
    sta, _ = _excute_cmd(cmd)
    return not bool(sta)

def _session_kill(name):
   _excute_cmd("tmux kill-session -t %s" % name)

def _attach_session(name):
    _excute_cmd("tmux -2 attach -t %s" % name)

def _detach_client(name):
    _excute_cmd("tmux detach-client")    

def _create_session(name, sess):
    if _session_exist(name):
        _detach_client(name)
        _session_kill(name)

    sess = TmuxSession(name, sess)
    sess.build()
    

class TmuxSession(object):
    """docstring for TmuxSession"""
    def __init__(self, name, dict):
        super(TmuxSession, self).__init__()
        self.name = name
        self.dict = dict
        #create tmux session
        sta, out = _excute_cmd("tmux new-session -s %s -n first -d" % self.name)


    def build(self):
        self.windows = self.dict.get('windows')
        for win in self.windows:
            self.__create_window(win)

    def __create_window(self, win):
        #create 
        win_name = win.get('window_name')
        sta, out = _excute_cmd("tmux new-window -n %s -t %s" % (win_name, self.name))
        #exceute cmd 
        cmds = win.get('init_cmd')
        for cmd in cmds:
            self.__excute_cmd(win_name, 0, cmd)

    def __excute_cmd(self, win, pane, cmd):
        f_cmd = "tmux send-keys -t %s:%s.%d \"%s\" C-m" % (self.name, win, pane, cmd)
        _excute_cmd(f_cmd)


def main():
    filename = parse_args()
    file_object = open(filename)
    try:
        all_the_text = file_object.read()
    finally:
        file_object.close()

    conf = jsdecode(all_the_text)
    for name, sess in conf.items():
        pprint(sess)
        _create_session(name, sess)

    _attach_session(name)   

if __name__ == '__main__':
    main()
