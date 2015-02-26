#!/usr/bin/python 
# -*- coding: utf-8 -*-

from json import JSONDecoder, JSONEncoder
from pprint import pprint
import commands
import optparse
import os

def jsencode(p):
    return JSONEncoder().encode(p)

def jsdecode(j):
    return JSONDecoder().decode(j)

def parse_args():
    usage = "usage: %prog [options]"
    parser = optparse.OptionParser(usage)

    parser.add_option("-c", help='The config file', action='store', dest='conf_file', default='~/.tcs.conf')

    options, args = parser.parse_args()
    return options.conf_file

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

        # 删除初始化的 window
        sta, out = _excute_cmd("tmux kill-window -t %s:first" % self.name)

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
    filename = os.path.expanduser(parse_args())
    file_object = open(filename)
    try:
        conf_text = file_object.read()
    except IOError, e:
        print 'No such file (%s)' % filename
    finally:
        file_object.close()

    conf = jsdecode(conf_text)
    for name, sess in conf.items():
        _create_session(name, sess)

    _attach_session(name)   

if __name__ == '__main__':
    main()
