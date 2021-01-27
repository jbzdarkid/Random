from pathlib import Path
import re
import sys

# https://en.wikipedia.org/wiki/X86_calling_conventions#List_of_x86_calling_conventions
CALLING_CONVENTION = 'x86 fastcall'

def strip(str):
  str = str.strip()

  is_byte = ('byte ptr' in str)
  m = re.search('\[.*?\]', str)
  if m:
    str = m.group(0)
  if is_byte:
    str = f'(byte){str}'

  m = re.search('\[esp ?\+ ?(.+)\]', str)
  if m:
    stack_offset = int(m.group(1), 16)
    if stack_offset % 4 != 0:
      return str # Uneven stack offset, unsure how to handle

    stack_offset = stack_offset // 4
    if stack_offset < len(function_stack):
      replace = function_stack[stack_offset]
    else:
      stack_offset -= len(function_stack)
      if stack_offset < len(stack):
        replace = stack[stack_offset]
      else:
        stack_offset -= len(stack)
        replace = f'arg_{stack_offset}'
    str = str[:m.start(0)] + replace + str[m.end(0):]
  return str

p = Path('raw.txt')
jumps = []
lines = {}
stack = []
function_stack = []
function_addr = None
is_function_stack = False
last_cmp = None

for line in p.open('r'):
  if line.count('|') != 3:
    continue
  addr, bytes, asm, comment = line.split('|')
  addr = addr.lstrip('0').strip()
  orig_asm = asm.strip()
  bytes = bytes.strip().replace(':', '').replace(' ', '')
  hex = []
  for i in range(0, len(bytes), 2):
    hex.append(int(bytes[i:i+2], 16))

  if not function_addr:
    function_addr = addr

  if orig_asm.count(' ') > 0:
    inst, asm = orig_asm.split(' ', 1)
  else:
    inst = orig_asm
    asm = ''
  asm = asm.lstrip()
  if inst == 'jmp':
    asm = asm.split('.')[-1]
    jumps.append(asm)
    asm = f'goto {asm}'
  elif inst in ['je', 'jne', 'ja', 'jae', 'jle', 'jb', 'jbe', 'jnz']:
    asm = asm.split('.')[-1]
    jumps.append(asm)
    assert(last_cmp)
    if inst not in last_cmp:
      asm = inst + '\t' + asm
      print(inst, last_cmp.keys())
    else:
      asm = f'if ({last_cmp[inst]}) goto {asm}'
    last_cmp = None # @Assume compilers do not make multiple jumps with the same flags
    is_function_stack = True
  elif inst in ['sar', 'shl', 'sal']:
    reg, amt = asm.split(',')
    amt = int(amt, 16)
    if amt <= 8:
      amt = 2 ** amt
    else:
      amt = f'(2 ^ {amt})'
    operand = {'sar': '/', 'shl': '*', 'sal': '*'}[inst]
    asm = f'{reg} = {reg} {operand} {amt}'
  elif inst == 'shr':
    reg, amt = asm.split(',')
    asm = f'{reg} = {reg} >> {int(amt, 16)} // Note: does not preserve sign'
  elif inst[:3] == 'mov':
    dst, src = asm.split(',')
    asm = f'{strip(dst)} = {strip(src)}'
  elif inst == 'lea':
    dst, src = asm.split(',')
    src = strip(src)
    if src[0] == '[' and src[-1] == ']':
      src = src[1:-1]
    else:
      src = '&' + src
    asm = f'{dst} = {src}'
  elif inst == 'imul':
    if asm.count(',') == 0:
      multiplier = asm
      if hex[0] == 0xF6:
        multiplicand = 'al'
        product = 'ax'
      elif hex[0] == 0x66:
        multiplicand = 'ax'
        product = 'dx:ax'
      elif hex[0] == 0xF7:
        multiplicand = 'eax'
        product = 'edx:eax'
      elif hex[0] == 0x48:
        multiplicand = 'rax'
        product = 'rdx:rax'
      else:
        assert(False)
      asm = f'{product} = {multiplicand} * {multiplier}'
    else:
      asm = isnt + '\t' + asm
  elif inst == 'xor':
    dst, src = asm.split(',')
    if dst == src:
      asm = f'{dst} = 0'
    else:
      asm = inst + '\t' + asm
  elif inst == 'inc':
    asm = f'{asm}++'
  elif inst == 'dec':
    asm = f'{asm}--'
  elif inst in ['test', 'cmp', 'sub', 'add']:
    dst, src = asm.split(',')
    dst = strip(dst)
    src = strip(src)
    asm = ''

    last_cmp = {}
    if inst == 'test' and dst == src:
      src = 0
    if inst in ['sub', 'add']:
      if inst == 'sub':
        asm = f'{dst} = {dst} - {src}'
      elif inst == 'add':
        asm = f'{dst} = {dst} - {src}'
      src = 0
      last_cmp = {
        'js': f'{dst} < {src}',
        'jns': f'{dst} >= {src}',
      }

    last_cmp.update({
      'je': f'{dst} == {src}',
      'jne': f'{dst} != {src}',
      'jl': f'{dst} < {src}',
      'jle': f'{dst} <= {src}',
      'jb': f'{dst} < {src}',
      'jbe': f'{dst} <= {src}',
      'jg': f'{dst} > {src}',
      'jge': f'{dst} >= {src}',
      'ja': f'{dst} > {src}',
      'jae': f'{dst} >= {src}',
    })
  elif inst == 'nop':
    asm = ''
  elif inst == 'ret':
    # TODO: Somehow restore the stack... As a workaround, I'm not popping registers from the stack!
    amt = int(asm, 16) if asm else 0
    amt = 0 # @Assume the compiler knows what it's doing
    asm = 'pop\n' * (amt // 4) + 'return'
  elif inst == 'push':
    if hex[0] == 0x6A:
      asm = '(byte)0x' + str(int(asm, 16)).zfill(2)
    if is_function_stack:
      function_stack.append(asm) # Technically this should be 'current value of' not just the register
    else:
      stack.append(asm)
    asm = ''
  elif inst == 'pop':
    if len(function_stack) > 0:
      function_stack.pop()
    else:
      pass
      # stack.pop()
    asm = ''
  elif inst == 'call':
    asm = asm.split('.')[-1]
    if CALLING_CONVENTION == 'x86 fastcall':
      args = 'ecx, edx, ' + ', '.join(reversed(function_stack))
    asm = f'func_{asm}({args})'
    if CALLING_CONVENTION in ['x86 fastcall']:
      function_stack = []
    else:
      pass # TODO: Non-callee saved conventions don't work like this.
  elif inst == 'rep':
    if asm == 'movsd':
      asm = '[edi] = [esi]\n  edi = edi + 4\n  esi = esi + 4'
    elif hex[1] == 0x48: # @Guess
      asm = '[rdi] = [rsi]\n  rdi = rdi + 8\n  rsi = rsi + 8'

  else:
    asm = inst + '\t' + asm

  if '--debug' in sys.argv:
    asm += ' ' * (60 - len(asm)) + orig_asm
    print(stack, orig_asm)
  lines[addr] = asm

addrs = sorted(lines.keys())
print(f'void func_{function_addr}() {{')
for addr in addrs:
  if addr in jumps:
    print(f'label {addr}:')
  if lines[addr]:
    print(f'  {lines[addr]}')
print('}')