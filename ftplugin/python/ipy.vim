" Vim integration with Cpyvke
"
" Copyright © 2016-2018 Cyril Desjouy <ipselium@free.fr>
" Distributed under terms of the BSD license.
"
" @author: Cyril Desjouy
"
" ADAPTED FROM : Paul Ivanov (http://pirsquared.org)
"
" 	* www.github.com/sophAi/vim-ipython_py3
" 	* www.github.com/ivanov/vim-ipython
"
"
" Check if python is available. If not, exit !
if !has('python3')
    finish
endif

" Allow custom mappings.
if !exists('g:ipy_perform_mappings')
    let g:ipy_perform_mappings = 1
endif

python3 << EOF
import vim
import sys
vim_cpyvke_path = vim.eval("expand('<sfile>:h')")
sys.path.append(vim_cpyvke_path)
from vim_cpyvke import *
EOF

" vim-cpyvke buffer
au CursorHold *.*,vim-cpyvke :python3 if update_subchannel_msgs(): vim_echo("IPython shell updated (on idle)",'Operator')

" Same as above, but on regaining window focus (mostly for GUIs)
au FocusGained *.*,vim-cpyvke :python3 if update_subchannel_msgs(): vim_echo("IPython shell updated (on input focus)",'Operator')

" Update vim-cpyvke buffer when we move the cursor there. A message is only
" displayed if vim-cpyvke buffer has been updated.
au BufEnter vim-cpyvke :python3 if update_subchannel_msgs(): vim_echo("IPython shell updated (on buffer enter)",'Operator')

" Setup plugin mappings for the most common ways to interact with ipython.
noremap <Plug>(IPython-AutoConnect)        :python3 connect_cpyvke_kernel()<CR>
noremap <Plug>(IPython-RunFile)            :python3 run_this_file()<CR>
noremap <Plug>(IPython-RunLine)            :python3 run_this_line()<CR>
noremap <Plug>(IPython-RunLines)           :python3 run_these_lines()<CR>
noremap <Plug>(IPython-CloseAll)           :python3 run_command("plt.close('all')")<CR>
noremap <Plug>(IPython-RunLineAsTopLevel)  :python3 dedent_run_this_line()<CR>
noremap <Plug>(IPython-RunLinesAsTopLevel) :python3 dedent_run_these_lines()<CR>
noremap <Plug>(IPython-UpdateShell)        :python3 if update_subchannel_msgs(force=True): vim_echo("IPython shell updated",'Operator')<CR>

if g:ipy_perform_mappings != 0
    map  <buffer> <silent> <C-c>c          <Plug>(IPython-AutoConnect)
    map  <buffer> <silent> <F5>            <Plug>(IPython-RunFile)
    map  <buffer> <silent> <F9>            <Plug>(IPython-RunLine)
    map  <buffer> <silent> <F10>           <Plug>(IPython-RunLines)
    map  <buffer> <silent> <LocalLeader>s  <Plug>(IPython-UpdateShell)
    imap <buffer> <silent> <F5>            <C-o><Plug>(IPython-RunFile)
    imap <buffer>          <F9>            <C-o><Plug>(IPython-RunLine)
    imap <buffer>          <F10>           <C-o><Plug>(IPython-RunLines)
    map  <buffer> <silent> <C-c><F9>       <Plug>(IPython-RunLineAsTopLevel)
    map  <buffer> <silent> <C-c><F10>      <Plug>(IPython-RunLinesAsTopLevel)
    map  <buffer> <silent> <C-c><F4>       <Plug>(IPython-CloseAll)
endif

command! -nargs=* IPython :py3 km_from_string("<args>")
command! -nargs=0 IPythonCpyvke :py3 connect_cpyvke_kernel()
command! -nargs=0 IPythonClipboard :py3 km_from_string(vim.eval('@+'))
command! -nargs=0 IPythonXSelection :py3 km_from_string(vim.eval('@*'))
command! -nargs=0 IPythonNew :py3 new_kernel()

