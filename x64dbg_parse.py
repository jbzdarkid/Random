from pathlib import Path
import re
import sys
from textwrap import dedent

# https://en.wikipedia.org/wiki/X86_calling_conventions#List_of_x86_calling_conventions
# CALLING_CONVENTION = 'x86 fastcall'
CALLING_CONVENTION = 'x86 thiscall'
ENDINNESS = 'little'

# TODO: Extend this table for x64. Or just replace it, since we need to use rax, etc.
# https://www.tortall.net/projects/yasm/manual/html/arch-x86-registers.html
register_replacements_x86 = {
  'al': '(byte)eax',
  'bl': '(byte)ebx',
  'cl': '(byte)ecx',
  'dl': '(byte)edx',
  'ah': '((eax & 0xFF00) / 0x100)',
  'bh': '((ebx & 0xFF00) / 0x100)',
  'ch': '((ecx & 0xFF00) / 0x100)',
  'dh': '((edx & 0xFF00) / 0x100)',
  'ax': '(short)eax',
  'bx': '(short)ebx',
  'cx': '(short)ecx',
  'dx': '(short)edx',
  'si': '(short)esi',
  'di': '(short)edi',
  'sp': '(short)esp',
  'bp': '(short)ebp',
}

register_replacements_x64 = {
  'sil':  '(byte)esi',
  'dil':  '(byte)edi',
  'bpl':  '(byte)ebp',
  'spl':  '(byte)esp',
  'r8b':  '(byte)r8',
  'r8w':  '(short)r8',
  'r8d':  '(int)r8',
}

def split(asm):
  dst, src = asm.split(',')
  return strip(dst), strip(src)

def strip(str):
  str = str.strip()

  if m := re.fullmatch('st\((\d+)\)', str):
    i = int(m.group(1))
    if len(fpu_stack) > i:
      str = fpu_stack[i]

  is_byte = ('byte ptr' in str)
  m = re.search('\[.*?\]', str)
  if m:
    str = m.group(0)
  if is_byte:
    str = f'(byte){str}'

  m = re.search('\[(?:e|r)sp ?\+ ?(.+)\]', str)
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

  str = register_replacements_x86.get(str, str) # Replace if found, unchanged if not.
  return str

reg_values = {
  'eax': 'orig_eax',
  'ebx': 'orig_ebx',
  'ecx': 'orig_ecx',
  'edx': 'orig_edx',
  'esi': 'orig_esi',
  'ebp': 'orig_ebp',
}
def assign(dst, src):
  for key in reg_values:
    if key in dst:
      reg_values[key] = src
  return f'{dst} = {src}'

def to_hex_str(num, len=8):
  import builtins
  assert(ENDINNESS == 'little')
  # TODO: return '0x' + builtins.hex(num)[2:].upper()
  return '0x' + builtins.hex(num)[2:].upper().zfill(len)

exe = r'C:\Program Files (x86)\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\DARKSOULS.exe'
with open(exe, 'rb') as f:
  assembly = f.read()
"""
static_loads = {}
for i, byte in enumerate(assembly):
  if byte == 0xA1:
    addr = int.from_bytes(assembly[i+1:i+5], byteorder=ENDINNESS)
  elif byte == 0x8B and assembly[i+1] in [0x1D, 0x0D, 0x15, 0x3D, 0x35, 0x25, 0x2D]:
    addr = int.from_bytes(assembly[i+2:i+6], byteorder=ENDINNESS)
  else:
    continue
  if addr not in static_loads:
    static_loads[addr] = {'sources': []}
  static_loads[addr]['sources'].append(to_hex_str(i + 0x400C00))
sorted_static_loads = sorted([(len(static_loads[addr]['sources']), addr, static_loads[addr]['sources']) for addr in static_loads])
for count, addr, sources in sorted_static_loads:
  print(f'addr: {to_hex_str(addr)} is loaded {count} times: [{", ".join(sources[:5])}]')
"""
def get_switch_statement(addr, inst, size, num_cases=16):
  addr = addr - 0x400C00 # Module base address...?
  cases = {}
  for i in range(num_cases):
    bytes = assembly[addr + i*size:addr + (i+1)*size]
    value = int.from_bytes(bytes, byteorder=ENDINNESS)
    if value not in cases:
      cases[value] = set()
    cases[value].add(i)

  # Sort by number of labels w/ the same value, breaking ties by the lowest case label
  sorted_cases = [(len(cases[value]), min(cases[value]), value) for value in cases]
  sorted_cases.sort()

  # Replace the largest (and therefore final) case label with 'default' -- this helps sparse jump tables.
  largest_value = sorted_cases[-1]

  output = ''
  for _, __, value in sorted_cases:
    if value == largest_value:
      output += 'default:\n'
    else:
      for label in sorted(cases[value]):
        output += f'case {label}:\n'
    output += inst + to_hex_str(value) + '\n'
    if inst == 'goto ':
      jumps.add(value)

  return output

p = Path('raw.txt')
jumps = set()
data_jumps = set()
lines = []
stack = []
function_stack = []
fpu_stack = ['st(0)']
is_function_stack = False
unreachable_code = False
code_is_data = False
data_bytes = []
df_flag = '+'

last_cmp_ = (None, None)
def last_cmp(type):
  global last_cmp_
  cmp = {
    'je': '==', 'sete': '==',
    'jne': '!=', 'setne': '!=', 'cmovne': '!=',
    'jl': '<', 'jb': '<', 'js': '<',
    'jle': '<=', 'jbe': '<=',
    'jg': '>', 'ja': '>',
    'jge': '>=', 'jae': '>=', 'jns': '>=',
    # jp, jnp
  }
  if type not in cmp:
    return f'FAILURE: Unknown comparison type {type}'
  dst, src = last_cmp_
  if dst is None or src is None:
    return 'FAILURE: Comparison has unknown dst/src'
  last_cmp_ = (None, None) # @Assume compilers do not make multiple jumps with the same flags
  return f'{dst} {cmp[type]} {src}'

for line in p.open('r'):
  if line.count('|') != 3:
    continue
  addr, bytes, orig_asm, comment = line.split('|')
  addr = int(addr, 16)
  bytes = bytes.strip().replace(':', '').replace(' ', '')
  hex = []
  for i in range(0, len(bytes), 2):
    hex.append(int(bytes[i:i+2], 16))

  orig_asm = orig_asm.strip()
  if orig_asm.count(' ') > 0:
    inst, asm = orig_asm.split(' ', 1)
  else:
    inst = orig_asm
    asm = ''
  asm = asm.lstrip()
  if inst == 'jmp':
    asm = asm.split('.')[-1]
    try:
      asm = int(asm, 16)
      jumps.add(asm)
      asm = f'goto {to_hex_str(asm)}'
    except ValueError:
      m = re.search('\[(.*?)\*4\+0x([\dA-F]+)\]', asm)
      if m:
        src = m.group(1)
        switch_start = int(m.group(2), 16)
        asm = f'switch({src}) {{\n'
        asm += get_switch_statement(switch_start, 'goto ', 4)
        asm += '}'
      else:
        asm = f'goto {asm}'

    # Code which follows an unconditional jump should not be interpreted, until we reach an instruction which can be jumped to.
    unreachable_code = True
  elif inst in ['je', 'jne', 'jl', 'jle', 'jb', 'jbe', 'jg', 'jge', 'ja', 'jae', 'jp', 'jnp', 'js', 'jns']:
    asm = int(asm.split('.')[-1], 16)
    jumps.add(asm)
    asm = f'if ({last_cmp(inst)}) goto {to_hex_str(asm)}'
    is_function_stack = True
  elif inst in ['setne', 'sete']:
    asm = f'if ({last_cmp(inst)}) ' + assign(asm, 0x01)
  elif inst in ['cmovne']:
    asm = f'if ({last_cmp(inst)}) ' + assign(dst, src)
  elif inst in ['sar', 'shl', 'sal']:
    reg, amt = asm.split(',')
    try:
      amt = int(amt, 16)
      if amt <= 8:
        amt = 2 ** amt
      else:
        amt = f'(2 ^ {amt}) // {to_hex_str(2**amt)}'
    except ValueError:
      pass
    operand = {'sar': '/', 'shl': '*', 'sal': '*'}[inst]
    asm = assign(reg, f'{reg} {operand} {amt}')
  elif inst == 'shr':
    reg, amt = asm.split(',')
    asm = assign(reg, f'{reg} >> {int(amt, 16)}') + ' // Note: does not preserve sign'
  elif inst[:3] == 'mov':
    dst, src = split(asm)
    note = ''
    try:
      amt = int(src, 16)
      if amt >= 0x80000000: # Negative number
        src = -(0x100000000 - amt)
      elif amt > 0x00100000: # Large number, may indicate multiplication offset. TODO: Just look for a subsequent mul/imul?
        note = f' // Note: Large value is actually 2^32 / {0x100000000 / amt}'
    except ValueError:
      pass
    asm = assign(dst, src) + note
  elif inst == 'lea':
    dst, src = split(asm)
    if src[0] == '[' and src[-1] == ']':
      src = src[1:-1]
    else:
      src = '&' + src
    asm = assign(dst, src)
  elif inst in ['imul', 'mul']: # TODO: imul is for signed integers. I should probably care about that.
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
    elif asm.count(',') == 1:
      multiplicand, multiplier = asm.split(',')
      product = multiplicand
    elif asm.count(',') == 2:
      product, multiplicand, multiplier = asm.split(',')
    asm = assign(product, f'{multiplicand} * {multiplier}')
    if inst == 'mul':
      asm += ' // Note: Unsigned multiplication'
  elif inst in ['inc', 'dec']:
    dst = strip(asm)
    op = {'inc': '+', 'dec': '-'}[inst]
    assign(dst, f'{dst} {op} 1')
    last_cmp_ = (dst, 0)
    asm = f'{dst}{op}{op}'
  elif inst == 'neg':
    asm = assign(asm, f'~{asm}')
  elif inst in ['test', 'cmp']:
    dst, src = split(asm)
    if inst == 'test' and dst == src:
      src = 0
    last_cmp_ = (dst, src)
    asm = ''
  elif inst in ['sub', 'add', 'and', 'or', 'xor']:
    dst, src = split(asm)
    if dst in ['esp', 'rsp']: # Special case for stack pointer modifications
      amt = int(src, 16)
      if inst == 'sub':
        for i in range(amt // 4):
          stack.append(f'local_{i}')
      elif inst == 'add':
        for _ in range(amt // 4):
          pass # stack.pop()
      asm = ''
    else:
      op = {'sub': '-', 'add': '+', 'and': '&', 'or': '|', 'xor': '^'}[inst]
      if inst == 'xor' and dst == src:
        asm = assign(dst, '0')
      elif inst == 'or' and src == '0xFFFFFFFF':
        asm = assign(dst, '-1')
      else:
        if inst in ['and', 'or']:
          try:
            amt = int(src, 16)
            if amt >= 0x80000000: # High bit is set, use 2's complement instead
              src = f'~{to_hex_str(0xFFFFFFFF - amt)}'
            else:
              src = to_hex_str(amt)
          except ValueError:
            pass # Register, not immediate
        asm = assign(dst, f'{dst} {op} {src}')
    last_cmp_ = (dst, 0)
  elif inst == 'nop':
    asm = ''
  elif inst == 'leave':
    asm = ''
  elif inst == 'ret':
    # TODO: Somehow restore the stack... As a workaround, I'm not popping registers from the stack!
    # Instead, we clear the stack after each call.
    # amt = int(asm, 16) if asm else 0
    # asm = 'pop\n' * (amt // 4) + 'return'
    # @Assume the compiler knows what it's doing
    asm = 'return ' + reg_values['eax']
    unreachable_code = True
  elif inst == 'int3':
    asm = ''
  elif inst == 'push':
    if hex[0] in [0x6A, 0x68]:
      if '.' in asm:
        asm = asm.split('.')[1]
      asm = to_hex_str(int(asm, 16))
    elif asm in reg_values:
      asm = reg_values[asm]
    if is_function_stack:
      function_stack.append(asm)
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
    try:
      asm = to_hex_str(int(asm, 16))
    except ValueError:
      pass
    args = []
    if CALLING_CONVENTION == 'x86 fastcall':
      args += [reg_values['ecx'], reg_values['edx']]
    elif CALLING_CONVENTION == 'x86 thiscall':
      args += [reg_values['ecx']]
    if len(function_stack) > 0:
      args += reversed(function_stack)
    asm = f"func_{asm}({', '.join(args)})"
    if CALLING_CONVENTION in ['x86 fastcall', 'x86 thiscall']:
      asm = 'eax = ' + asm
      function_stack = []
  elif inst == 'rep':
    if asm == 'stosb':
      size = 1
      source = 'al'
      dest = 'edi' # Not sure. Maybe di?
    elif asm == 'stosw':
      size = 2
      source = 'ax'
      dest = 'edi' # Not sure. Maybe di?
    elif asm == 'stosd':
      size = 4
      source = 'eax'
      dest = 'edi'
    elif asm == 'stosq':
      size = 8
      source = 'rax'
      dest = 'rdi'
    asm = dedent(f'''\
        for(; ecx > 0; ecx--) {{
          [es:{dest}] = {source}
          {dest} = {dest} {df_flag} 1
        }}''')
  elif inst == 'cld':
    df_flag = '+'
    asm = ''
  elif inst == 'std':
    df_flag = '-' # Reverses the direction of 'rep' instructions
    asm = ''
  elif inst == 'xorps':
    dst, src = split(asm)
    if dst == src:
      asm = assign(dst, '0')
    else:
      asm = inst + '\t' + asm
  elif inst == 'comiss':
    last_cmp_ = split(asm)
    asm = ''
  elif inst in ['fild', 'fld']:
    dst, src = split(asm)
    fpu_stack.insert(0, src)
    asm = ''
  elif inst == 'fldz':
    fpu_stack.insert(0, '0.0f')
    asm = ''
  elif inst in ['fadd', 'faddp', 'fiadd', 'fsub', 'fsubp', 'subsd', 'fmul', 'fmulp']:
    dst, src = split(asm)
    if inst in ['fiadd']:
      src = f'(float){src}'
    last_cmp_ = (dst, src)
    op = {'fadd': '+', 'faddp': '+', 'fiadd': '+', 'fsub': '-', 'fsubp': '-', 'subsd': '-', 'fmul': '*', 'fmulp': '*'}[inst]
    asm = assign(dst, f'{dst} {op} {src}')
    if inst in ['faddp', 'fsubp', 'fmulp'] and len(fpu_stack) > 0:
      fpu_stack.pop(0)
  elif inst in ['fst', 'fstp', 'fistp']:
    dst, src = split(asm)
    if inst == 'fistp':
      src = f'(float){src}'
    asm = assign(dst, src)
    if inst == 'fstp' and len(fpu_stack) > 0:
      fpu_stack.pop(0)
  elif inst in ['cvtps2pd']:
    dst, src = split(asm)
    asm = assign(dst, f'(double){src}') + ' // Convert float to double'
  elif inst in ['cvtpd2ps', 'cvttsd2si']:
    dst, src = split(asm)
    asm = assign(dst, f'(float){src}') + ' // Convert double to float'
  elif inst == 'fxch':
    dst, src = split(asm)
    asm = assign(dst, src) + '\n' + assign(src, dst)


  else:
    print(f'Missing instruction: {inst}')
    asm = inst + '\t' + asm

  if '--debug' in sys.argv:
    asm += ' ' * (60 - len(asm)) + orig_asm
  lines.append((addr, asm))

first_addr = lines[0][0]

jumps = sorted(jumps.union(data_jumps))
print(f'void func_{to_hex_str(first_addr)}() {{')
for addr, asm in lines:
  if addr in jumps:
    print(f'label {to_hex_str(addr)}:')
    jumps.remove(addr)
  if len(jumps) > 0 and addr > jumps[0]:
    print(f'label {to_hex_str(addr)}: // Note {to_hex_str(jumps[0])} occurred in the middle of the previous line')
    jumps.pop(0)
  if asm:
    if '--debug' in sys.argv:
      print(f'{to_hex_str(addr)}: {asm}')
    else:
      for line in asm.split('\n'):
        if '--label' in sys.argv:
          print(to_hex_str(addr), end=':')
        print(f'  {line}')
print('}')

if len(jumps) > 0:
  print(f'WARNING: {len(jumps)} jumps were not matched in the assembly! Please disassemble a larger region.')
  print(f'Region: {to_hex_str(first_addr)}-{to_hex_str(lines[-1][0])}')
  print('[' + ', '.join(map(to_hex_str, sorted(jumps))) + ']')