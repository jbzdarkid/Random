version 6.0
if &cp | set nocp | endif
"set background=dark
set backspace=indent,eol,start
set backup
set cindent
set copyindent
set diffexpr=MyDiff()
set display=truncate
set guioptions=egmrLT
set helplang=En
set history=200
set hlsearch
set ignorecase
set incsearch
set keymodel=startsel,stopsel
set preserveindent
set runtimepath=~/vimfiles,C:\\Program\ Files\ (x86)\\Vim/vimfiles,C:\\Program\ Files\ (x86)\\Vim\\vim80,C:\\Program\ Files\ (x86)\\Vim\\vim80\\pack\\dist\\opt\\matchit,C:\\Program\ Files\ (x86)\\Vim/vimfiles/after,~/vimfiles/after
set scrolloff=5
set selection=exclusive
set selectmode=mouse,key
set shiftround
set shiftwidth=4
set smartcase
set smartindent
set tabstop=4
set ttimeout
set ttimeoutlen=100
set undofile
set visualbell
set whichwrap=b,s,<,>,[,]
set wildmenu
"set window=39
set lines=60 columns=120
syntax enable
colorscheme slate
behave xterm
imap <Down> <C-o>gj
imap <Up> <C-o>gk
nmap <Down> gj
nmap <Up> gk
