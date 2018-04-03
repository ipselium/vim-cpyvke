- - -

# vim-cpyvke

**vim-cpyvke** is a *vim* plugin that provides a kind of integration of IPython
and **cpyvke** (www.github.com/ipselium/cpyvke) to *vim*. This plugin is a
minimal version of Paul Ivanov's **vim-ipython** plugin :

* www.github.com/ivanov/vim-ipython
* www.github.com/sophAi/vim-ipython_py3

**vim-cpyvke** provides tools to evaluate blocks of code or full scripts
directly from vim. The duo **cpyvke/vim-cpyvke** paired with a vim plugin such
as **python-mode** (www.github.com/klen/python-mode) can provide a complete
development environment for Python in console.

- - -

## Installation with Vundle

Install **vim-cpyvke** with vundle. Add

`Plugin 'ipselium/vim-cpyvke'`

to your vimrc, then

`:BundleInstall`

## Quick Start

First, start **cpyvke**, then open a Python script with *vim*. Following
shortcuts are now available in vim:

* `C-c c` : Autoconnect to same kernel as **cpyvke**
* `F5` : Run the current buffer
* `F9`: Run the current line
* `F10`: Run the selected lines (in visual mode)

- - -

## Requirement

* cpyvke : www.github.com/ipselium/cpyvke

- - -

## Dependencies

* Ipython >= 5.1
* ipykernel (tested with 4.6.1)
* jupyter_client >= 4.4


