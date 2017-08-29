autocmd FileType gitcommit setlocal spell "Spell check on git commit messages
match ErrorMsg '\s\+$' "Highlight EOL whitespace as error
if &cp | set nocp | endif

"Colorscheme (Changes as needed)
highlight ErrorMsg guibg='LightRed' guifg='LightRed'
au InsertEnter * hi StatusLine term=reverse ctermbg=darkgreen
au InsertLeave * hi StatusLine term=reverse ctermbg=green
hi clear
hi ColorColumn ctermbg=darkred
hi Comment ctermfg=darkgray
hi Constant ctermfg=darkmagenta
hi Statement ctermfg=green
hi LineNr ctermfg=green
hi clear CursorLine
hi CursorLineNr ctermfg=white
hi PreProc ctermfg=darkgreen
set cursorline
syntax enable

set backspace=indent,eol,start
set backup
set cindent
set colorcolumn=80
set copyindent
set diffopt+=iwhite
set expandtab
set guioptions=egmrLT
set helplang=En
set history=200
set hlsearch
set ignorecase
set incsearch
set keymodel=startsel,stopsel
set laststatus=2
set number
set preserveindent
set ruler
set runtimepath=~/vimfiles,C:\\Program\ Files\ (x86)\\Vim/vimfiles,C:\\Program
set scrolloff=5
set selection=exclusive
set selectmode=mouse,key
set shiftround
set shiftwidth=2
set smartcase
set smartindent
set smarttab
set statusline=%<%f\ %h\ %m%=%4v\ %4l\ %P
set ttimeout
set ttimeoutlen=100
set undofile
set visualbell
set whichwrap=b,s,<,>,[,]
set wildmenu
set lines=80 columns=240
if version >= 800
  set display=truncate
endif
"Affects the way selections work in visual modes
behave xterm
"Multiline traversal
inoremap <Down> <C-o>gj
nnoremap <Down> gj
vnoremap <Down> gj
inoremap <Up> <C-o>gk
nnoremap <Up> gk
vnoremap <Up> gk
"Binds Shift-U to undo
nnoremap <S-u> <C-R>
"Binds Tab/Shift-Tab to indent/unindent
inoremap <S-Tab> <C-o><<
inoremap <Tab> <C-o>>>
"Trying to fix a bug with shift-up
vnoremap <S-Up> <Up>
vnoremap <S-Down> <Down>
