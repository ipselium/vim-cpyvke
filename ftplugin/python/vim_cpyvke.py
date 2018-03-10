#! /usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Adapted from Paul Ivanov's vim-ipython
#       * http://pirsquared.org
#       * www.github.com/sophAi/vim-ipython_py3
#       * www.github.com/ivanov/vim-ipython
#
# Copyright © Paul Ivanov
# Copyright © 2016-2018 Cyril Desjouy <ipselium@free.fr>
#
# This file is part of vim-cpyvke
#
# vim_cpyvke is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# vim_cpyvke is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with vim_cpyvke. If not, see <http://www.gnu.org/licenses/>.
#
#
# Creation Date : mar. 06 mars 2018 17:27:32 CET
# Last Modified : mer. 05 mars 2018 00:43:47 CET
"""
-----------
DOCSTRING

@author: Cyril Desjouy
"""

import re
import os
from queue import Empty

try:
    import vim
except ImportError:
    class NoOp(object):
        def __getattribute__(self, key):
            return lambda *args: '0'
    vim = NoOp()
    print("Uh oh, not running inside vim")

try:
    from jupyter_client import KernelManager, find_connection_file
except ImportError:
    raise ImportError("Could not find jupyter_client. ")


show_execution_count = True  # wait to get numbers for In[43]: feedback?
monitor_subchannel = True    # update vim-ipython 'shell' on every send?
run_flags = "-i"             # flags to for IPython's run magic when using <F5>


# from http://serverfault.com/questions/71285/in-centos-4-4-how-can-i-strip-escape-sequences-from-a-text-file
strip = re.compile('\x1B\[([0-9]{1,2}(;[0-9]{1,2})?)?[m|K]')

# get around unicode problems when interfacing with vim
vim_encoding = vim.eval('&encoding') or 'utf-8'


def vim_echo(arg, style="Question"):
    try:
        vim.command("echohl {}".format(style))
        vim.command("echom \"{}\"".format(arg.replace('\"', '\\\"')))
        vim.command("echohl None")
    except vim.error:
        print("-- {}".format(arg))


def vim_variable(name, default=None):
    exists = int(vim.eval("exists('{}')".format(name)))
    return vim.eval(name) if exists else default


def vim_regex_escape(x):
    for old, new in (("[", "\\["), ("]", "\\]"), (":", "\\:"),
                     (".", "\."), ("*", "\\*")):
        x = x.replace(old, new)
    return x


# status buffer settings
status_prompt_in = vim_variable('g:ipy_status_in', 'In [%(line)d]: ')
status_prompt_out = vim_variable('g:ipy_status_out', 'Out[%(line)d]: ')

status_prompt_colors = {
    'in_ctermfg': vim_variable('g:ipy_status_in_console_color', 'Green'),
    'in_guifg': vim_variable('g:ipy_status_in_gui_color', 'Green'),
    'out_ctermfg': vim_variable('g:ipy_status_out_console_color', 'Red'),
    'out_guifg': vim_variable('g:ipy_status_out_gui_color', 'Red'),
    'out2_ctermfg': vim_variable('g:ipy_status_out2_console_color', 'Gray'),
    'out2_guifg': vim_variable('g:ipy_status_out2_gui_color', 'Gray'),
}

status_blank_lines = int(vim_variable('g:ipy_status_blank_lines', '1'))

try:
    kc
    km
except NameError:
    kc = None
    km = None


def new_kernel():
    """
    Create a new IPython kernel (optionally with extra arguments)
    """

    km = KernelManager()
    km.start_kernel()
    return km_from_string(km.connection_file)


def connect_cpyvke_kernel():
    cpyvke_cf = os.path.expanduser('~') + '/.cpyvke/LastKernel'
    if os.path.exists(cpyvke_cf):
        with open(cpyvke_cf, 'r') as f:
            cf = f.read().split("\n")[-2].lstrip().split(' ')[-1]
        return km_from_string(cf)
    else:
        vim_echo('Kernel not found (See ~/.cpyvke/LastKernel)', 'Error')


def km_from_string(s=''):
    """
    Create kernel manager.
    """

    global km, kc, send

    s = s.replace('--existing', '')

    try:
        if '--profile' in s:
            k, p = s.split('--profile')
            k = k.lstrip().rstrip()  # kernel part of the string
            p = p.lstrip().rstrip()  # profile part of the string
            fullpath = find_connection_file(k, p)
        elif s == '':
            fullpath = find_connection_file()
        else:
            fullpath = find_connection_file(s.lstrip().rstrip())
    except IOError:
        vim_echo(":IPython " + s + " failed", "Info")
        vim_echo("^-- failed '" + s + "' not found", "Error")
        return

    km = KernelManager(connection_file=fullpath)
    km.load_connection_file()
    kc = km.client()
    kc.start_channels()
    send = kc.execute
    vim_echo('Connected to {}'.format(fullpath))


def strip_color_escapes(s):
    return strip.sub('', s)


def vim_ipython_is_open():
    """
    Helper function to let us know if the vim-ipython shell is currently
    visible
    """
    for w in vim.windows:
        if w.buffer.name is not None and w.buffer.name.endswith("vim-cpyvke"):
            return True
    return False


def update_subchannel_msgs(debug=False, force=False):
    """
    Grab any pending messages and place them inside the vim-ipython shell.
    This function will do nothing if the vim-ipython shell is not visible,
    unless force=True argument is passed.
    """

    if kc is None or (not vim_ipython_is_open() and not force):
        return False

    # Create vim-cpyvke buffer if not already started
    startedin_vimipython = vim.eval('@%') == 'vim-cpyvke'
    if not startedin_vimipython:
        # switch to preview window
        vim.command(
            "try"
            "|silent! wincmd P"
            "|catch /^Vim\%((\a\+)\)\=:E441/"
            "|silent pedit +set\ ma vim-cpyvke"
            "|silent! wincmd P"
            "|endtry")
        # if the current window is called 'vim-cpyvke'
        if vim.eval('@%') == 'vim-cpyvke':
            # set the preview window height to the current height
            vim.command("set pvh=" + vim.eval('winheight(0)'))
        else:
            # close preview window, it was something other than 'vim-cpyvke'
            vim.command("pcl")
            vim.command("silent pedit +set\ ma vim-cpyvke")
            # switch to preview window
            vim.command("wincmd P")
            # subchannel window quick quit key 'q'
            vim.command('nnoremap <buffer> q :q<CR>')
            vim.command("set bufhidden=hide buftype=nofile ft=python")
            # don't come up in buffer lists
            vim.command("setlocal nobuflisted")
            # no folders
            vim.command("setlocal foldlevel=99")
            # no line numbers, we have in/out nums
            vim.command("setlocal nonumber")
            # no swap file (so no complaints cross-instance)
            vim.command("setlocal noswapfile")

    # Syntax highlighting for python prompt
    colors = status_prompt_colors
    vim.command("hi IPyPromptIn ctermfg={} guifg={}".format(colors['in_ctermfg'],
                                                            colors['in_guifg']))
    vim.command("hi IPyPromptOut ctermfg={} guifg={}".format(colors['out_ctermfg'],
                                                             colors['out_guifg']))
    vim.command("hi IPyPromptOut2 ctermfg={} guifg={}".format(colors['out2_ctermfg'],
                                                              colors['out2_guifg']))
    in_expression = vim_regex_escape(status_prompt_in % {'line': 999}).replace('999', '[ 0-9]*')
    vim.command("syn match IPyPromptIn /^%s/" % in_expression)
    out_expression = vim_regex_escape(status_prompt_out % {'line': 999}).replace('999', '[ 0-9]*')
    vim.command("syn match IPyPromptOut /^%s/" % out_expression)
    vim.command("syn match IPyPromptOut2 /^\\.\\.\\.* /")

    b = vim.current.buffer
    update_occured = False
    msgs = kc.iopub_channel.get_msgs()

    cpyvke_code = ['whos', "np.save('/tmp/tmp_", 'fcpyvke0']

    for m in msgs:
        s = ''

        if 'msg_type' not in m['header']:
            continue

        header = m['header']['msg_type']

        if header == 'status':
            continue
        elif header == 'stream':
            if 'Data/Info' in m['content']['text']:
                continue
            else:
                s = strip_color_escapes(m['content']['text'])
        elif header == 'pyout' or header == 'execute_result':
            s = status_prompt_out % {'line': m['content']['execution_count']}
            s += m['content']['data']['text/plain']
        elif header == 'display_data':
            s += m['content']['data']['text/plain']
        elif header == 'pyin' or header == 'execute_input':
            # If it is one of cpyvke interaction, skip !
            if [i for i in cpyvke_code if i in m['content']['code']]:
                continue
            else:
                line_number = m['content'].get('execution_count', 0)
                prompt = status_prompt_in % {'line': line_number}
                s = prompt
            # add a continuation line (with trailing spaces if the prompt has them)
            dots = '.' * len(prompt.rstrip())
            dots += prompt[len(prompt.rstrip()):]
            s += m['content']['code'].rstrip().replace('\n', '\n' + dots)
        elif header == 'pyerr' or header == 'error':
            c = m['content']
            s = "\n".join(map(strip_color_escapes, c['traceback']))
            s += c['ename'] + ":" + c['evalue']

        if s.find('\n') == -1:
            # somewhat ugly unicode workaround from
            # http://vim.1045645.n5.nabble.com/Limitations-of-vim-python-interface-with-respect-to-character-encodings-td1223881.html
            if isinstance(s, str):
                s = s.encode(vim_encoding)
            b.append(s)
        else:
            try:
                b.append(s.splitlines())
            except:
                b.append([l.encode(vim_encoding) for l in s.splitlines()])
        update_occured = True

    # make a newline so we can just start typing there
    if status_blank_lines:
        if b[-1] != '':
            b.append([''])
    if update_occured or force:
        vim.command('normal! G')    # go to the end of the file
    if not startedin_vimipython:
        vim.command('normal! p')  # go back to where you were

    return update_occured


def get_child_msg(msg_id):
    while True:
        # get_msg will raise with Empty exception if no messages since 1 second
        m = kc.shell_channel.get_msg(timeout=1)
        if m['parent_header']['msg_id'] == msg_id:
            break
        else:
            # got a message, but not the one we were looking for
            vim_echo('Skipping a message on shell_channel', 'WarningMsg')
    return m


def print_prompt(prompt, msg_id=None):
    """
    Print In[] or In[42] style messages.
    """

    global show_execution_count

    if show_execution_count and msg_id:
        # wait to get message back from kernel
        try:
            child = get_child_msg(msg_id)
            count = child['content']['execution_count']
            vim_echo("In[{}]: {}".format(count, prompt))
        except Empty:
            vim_echo("In[]: {} (no reply from IPython kernel)".format(prompt))
    else:
        vim_echo("In[]: {}".format(prompt))


def with_subchannel(f, *args):
    """
    Conditionally monitor subchannel.
    """
    def f_with_update(*args):
        try:
            f(*args)
            if monitor_subchannel:
                update_subchannel_msgs(force=True)
        except NameError:  # Send not defined
            vim_echo("Not connected to IPython", 'Error')
    return f_with_update


@with_subchannel
def run_command(cmd):
    msg_id = send(cmd)
    print_prompt(cmd, msg_id)


@with_subchannel
def run_this_file():
    msg_id = send('%%run %s %s' % (run_flags, repr(vim.current.buffer.name),))
    print_prompt("In[]: %%run %s %s" % (run_flags,
                                        repr(vim.current.buffer.name)), msg_id)


@with_subchannel
def run_this_line(dedent=False):
    line = vim.current.line
    if dedent:
        line = line.lstrip()
    msg_id = send(line)
    print_prompt(line, msg_id)


@with_subchannel
def run_these_lines(dedent=False):
    r = vim.current.range
    if dedent:
        lines = list(vim.current.buffer[r.start:r.end+1])
        nonempty_lines = [x for x in lines if x.strip()]
        if not nonempty_lines:
            return
        first_nonempty = nonempty_lines[0]
        leading = len(first_nonempty) - len(first_nonempty.lstrip())
        lines = "\n".join(x[leading:] for x in lines)
    else:
        lines = "\n".join(vim.current.buffer[r.start:r.end+1])
    msg_id = send(lines)

    prompt = "lines {}-{} ".format(r.start+1, r.end+1)
    print_prompt(prompt, msg_id)


def dedent_run_this_line():
    run_this_line(True)


def dedent_run_these_lines():
    run_these_lines(True)
