autocmd FileType gitcommit setlocal spell "Spell check on git commit messages
autocmd FileType txt setlocal spell "Spell check on all .txt files
autocmd FileType md setlocal spell "Spell check on all .txt files
match ErrorMsg '\s\+$' "Highlight EOL whitespace as error
if &cp | set nocp | endif

"Colorscheme (Changes as needed)
highlight ErrorMsg guibg='LightRed' guifg='LightRed'
au InsertEnter * hi StatusLine term=reverse ctermbg=darkgreen
au InsertLeave * hi StatusLine term=reverse ctermbg=green
hi clear CursorLine
hi ColorColumn  ctermfg=none        ctermbg=darkred
hi Comment      ctermfg=darkgray    ctermbg=none
hi Constant     ctermfg=darkmagenta ctermbg=none
hi CursorLineNr ctermfg=white       ctermbg=none
hi LineNr       ctermfg=green       ctermbg=none
hi PreProc      ctermfg=darkgreen   ctermbg=none
hi Search       ctermfg=none        ctermbg=lightblue
hi Statement    ctermfg=brown       ctermbg=none
hi Type         ctermfg=blue        ctermbg=none
set cursorline
syntax enable

set autochdir
set backspace=indent,eol,start
set cindent
set colorcolumn=120
"set copyindent
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
"set preserveindent
set scrolloff=5
set selection=inclusive "Exclusive might be better?
set shiftround
set shiftwidth=2
set smartcase
set smartindent
set smarttab
set splitright
set splitbelow
set statusline=%<%f\ %h\ %m%=%4v\ %4l\ %P
set ttimeout
set ttimeoutlen=100
set visualbell
set whichwrap=b,s,<,>,[,]
set wildmenu
set lines=80 columns=249

"Larger window for vimdiff
if &diff
  set lines=100 columns=300
  set diffopt+=iwhite
endif

"Jump to the last position when reopening a file
if has("autocmd")
  au BufReadPost * if line("'\"") > 1 && line("'\"") <= line("$") | exe "normal! g'\""
endif

"Affects the way selections work in visual modes
behave xterm

inoremap <Down> <C-o>gj
nnoremap <Down>      gj
vnoremap <Down>      gj
inoremap <Up>   <C-o>gk
nnoremap <Up>        gk
vnoremap <Up>        gk

"Bind tab and shift-tab to adjust spacing (not enter a tab character)
inoremap <Tab> <C-T>
vnoremap <Tab> >
inoremap <S-Tab> <C-D>
vnoremap <S-Tab> <

"Binds Shift-U to undo
nnoremap <S-u> <C-R>

"Binds Control-C to copy, Control-V to paste, and Control-X to cut (with the system clipboard)
vnoremap <C-c> "+y
inoremap <C-v> <C-O>"+p
