from pathlib import Path
import re
import sys
from textwrap import dedent

# TODO: Consider switching to capstone
"""
import capstone

CODE = b"\x55\x48\x8b\x05\xb8\x13\x00\x00"

md = capstone.Cs(CS_ARCH_X86, CS_MODE_64)
for i in md.disasm(CODE, 0x1000): // 0x1000 == start point
  print("0x%x:\t%s\t%s" %(i.address, i.mnemonic, i.op_str))
  # i.address = 0x1000 (= addr)
  # i.mnemonic = "mov rax, ..." (= orig_asm)
  # i.bytes = 0x01, 0x02, 0x03 (= hex)
"""

# https://en.wikipedia.org/wiki/X86_calling_conventions#List_of_x86_calling_conventions
CALLING_CONVENTION = 'x86 fastcall'
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

  str = register_replacements_x86.get(str, str) # Replace if found, unchanged if not.
  return str

def to_hex_str(num, len=8):
  import builtins
  assert(ENDINNESS == 'little')
  return '0x' + builtins.hex(num)[2:].upper().zfill(len)

exe = r'C:\Program Files (x86)\Steam\steamapps\common\Dark Souls Prepare to Die Edition\DATA\DARKSOULS.exe'
with open(exe, 'rb') as f:
  assembly = f.read()

# for i in range(len(assembly)):
#   if assembly[i:i+8] == b'\xB7\xCD\x58\x00\xF7\xCD\x58\x00':
#     print(to_hex_str(i))

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
is_function_stack = False
last_cmp = None
unreachable_code = False
code_is_data = False
data_bytes = []
df_flag = '+'

for line in p.open('r'):
  if line.count('|') != 3:
    continue
  addr, bytes, orig_asm, comment = line.split('|')
  addr = int(addr, 16)
  bytes = bytes.strip().replace(':', '').replace(' ', '')
  hex = []
  for i in range(0, len(bytes), 2):
    hex.append(int(bytes[i:i+2], 16))

  if unreachable_code or code_is_data:
    if addr in jumps:
      unreachable_code = False
      code_is_data = False
    elif addr in data_jumps or addr-4 in data_jumps:
      # Slight hack, but it seems like some data arrays start at 1 (!)
      unreachable_code = False
      code_is_data = True

  if code_is_data or unreachable_code:
    needs_reassembly = False
    for byte in hex:
      if code_is_data:
        data_bytes.append(byte)
        if len(data_bytes) == 4:
          int_val = int.from_bytes(data_bytes, byteorder=ENDINNESS)
          jumps.add(int_val)
          lines.append((addr-3, f'// {to_hex_str(addr-3)}: {to_hex_str(int_val)}'))
          data_bytes = []
      if addr in jumps:
        needs_reassembly = True
        break
      addr += 1
    if needs_reassembly:
      lines.append((addr, f'// Please re-assemble the code from address {to_hex_str(addr)}'))
      break
    continue

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
  elif inst in ['je', 'jne', 'jl', 'jle', 'jb', 'jbe', 'jg', 'jge', 'ja', 'jae']:
    asm = int(asm.split('.')[-1], 16)
    jumps.add(asm)
    assert(last_cmp)
    if inst not in last_cmp:
      asm = inst + '\t' + asm
      print(inst, last_cmp.keys())
    else:
      asm = f'if ({last_cmp[inst]}) goto {to_hex_str(asm)}'
    last_cmp = None # @Assume compilers do not make multiple jumps with the same flags
    is_function_stack = True
  elif inst in ['setne']:
    assert(last_cmp)
    inst = {'setne':'jne'}[inst]
    if inst not in last_cmp:
      asm = inst + '\t' + asm
      print(inst, last_cmp.keys())
    else:
      asm = f'if ({last_cmp[inst]}) {asm} = 0x01'
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
    asm = f'{reg} = {reg} {operand} {amt}'
  elif inst == 'shr':
    reg, amt = asm.split(',')
    asm = f'{reg} = {reg} >> {int(amt, 16)} // Note: does not preserve sign'
  elif inst[:3] == 'mov':
    dst, src = asm.split(',')
    dst = strip(dst)
    src = strip(src)
    asm = f'{dst} = {src}'
    try:
      amt = int(src, 16)
      if amt > 0x0100000: # Large number, may indicate multiplication offset. TODO: Just look for a subsequent mul/imul?
        asm += f' // Note: Large value is actually 2^32 / {0x100000000 / amt}'
    except ValueError:
      pass
  elif inst == 'lea':
    dst, src = asm.split(',')
    src = strip(src)
    if src[0] == '[' and src[-1] == ']':
      src = src[1:-1]
    else:
      src = '&' + src
    asm = f'{dst} = {src}'
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
      asm = f'{product} = {multiplicand} * {multiplier}'
      if inst == 'mul':
        asm += ' // Note: Unsigned multiplication'
    else:
      asm = isnt + '\t' + asm
  elif inst == 'inc':
    asm = f'{asm}++'
  elif inst == 'dec':
    asm = f'{asm}--'
  elif inst == 'neg':
    asm = f'{asm} = ~{asm}'
  elif inst in ['test', 'cmp', 'sub', 'add', 'and', 'or', 'xor']:
    dst, src = asm.split(',')
    dst = strip(dst)
    src = strip(src)
    asm = ''

    last_cmp = {}
    if inst == 'test' and dst == src:
      src = 0
    if inst in ['sub', 'add', 'and', 'or', 'xor']:
      op = {'sub': '-', 'add': '+', 'and': '&', 'or': '|', 'xor': '^'}[inst]
      if inst in ['and', 'or']:
        try:
          src = to_hex_str(int(src, 16))
        except ValueError:
          pass # Register, not immediate
      if inst == 'xor' and dst == src:
        asm = f'{dst} = 0'
      elif inst == 'or' and src == '0xFFFFFFFF':
        asm = f'{dst} = -1'
      elif dst == 'esp':
        amt = int(src, 16)
        asm = ''
        if inst == 'sub':
          for i in range(amt // 4):
            stack.append(f'local_{i}')
        elif inst == 'add':
          for _ in range(amt // 4):
            pass
            # stack.pop()
      else:
        asm = f'{dst} = {dst} {op} {src}'
      src = 0
      last_cmp.update({
        'js': f'{dst} < {src}',
        'jns': f'{dst} >= {src}',
      })

    # Note: Comparison with overflow
    # To distribute addition across a modulo operation (e.g. cast to short), use the following template:
    # (short)(x + A) > B  is equivalent to
    # (x > B - A && x < 0x10000 - A) || (x > B - A + 0x10000)
    #
    # (short)(x + A) < B  is equivalent to
    # (x < B - A) || (x >= 0x10000 - A && x < B + 0x10000 - A)


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
      'regs': (dst, src),
    })
  elif inst == 'nop':
    asm = ''
  elif inst == 'leave':
    asm = ''
  elif inst == 'ret':
    # TODO: Somehow restore the stack... As a workaround, I'm not popping registers from the stack!
    # amt = int(asm, 16) if asm else 0
    amt = 0 # @Assume the compiler knows what it's doing
    asm = 'pop\n' * (amt // 4) + 'return'
    unreachable_code = True
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
      args = 'ecx, edx'
      if len(function_stack) > 0:
        args += ', ' + ', '.join(reversed(function_stack))
    asm = f'func_{asm}({args})'
    if CALLING_CONVENTION in ['x86 fastcall']:
      function_stack = []
    else:
      pass # TODO: Non-callee saved conventions don't work like this.
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
    dst, src = asm.split(',')
    if dst == src:
      asm = f'{dst} = 0'
    else:
      asm = inst + '\t' + asm
  elif inst == 'comiss':
    dst, src = asm.split(',')
    asm = ''
    last_cmp = {
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
    }
  elif inst in ['fldz', 'fstp']: # I'm sure these do something, but I can't tell what. So, I'm ignoring them until I figure it out.
    asm = ''

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