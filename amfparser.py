from struct import unpack, pack

# https://www.adobe.com/content/dam/acom/en/devnet/pdf/amf0-file-format-specification.pdf
TYPE_NUMBER  = 0
TYPE_BOOLEAN = 1
TYPE_STRING  = 2
TYPE_OBJECT  = 3
# UNUSED     = 4
TYPE_NULL    = 5
TYPE_UNDEF   = 6
TYPE_REFRNCE = 7
TYPE_EARRAY  = 8
TYPE_OBJ_END = 9
TYPE_SARRAY  = 10
TYPE_DATE    = 11
TYPE_LSTRING = 12
TYPE_UNSUPP  = 13
TYPE_RECORD  = 14
TYPE_XML_DOC = 15
TYPE_TYPEOBJ = 16
TYPE_AMF3    = 17

class Bytes():
  def __init__(self, file):
    self.file = file
    with file.open('rb') as f:
      self.bytes = f.read()
      self.i = 0

  def write_to_disk(self):
    with self.file.open('wb') as f:
      f.write(self.bytes)

  # Raises a ValueError if bytes is not found (note: it may be behind you)
  def seek(self, bytes):
    self.i = self.bytes.index(bytes) + len(bytes)

  def read_byte(self):
    self.i += 1
    return self.bytes[self.i-1]

  def read_bytes(self, count):
    self.i += count
    return self.bytes[self.i-count:self.i]

  def write_bytes(self, bytes):
    self.bytes = self.bytes[:self.i] + bytes + self.bytes[self.i + len(bytes):]
    self.i += len(bytes)

  def amf0_read(self):
    type = self.read_byte()

    if type == TYPE_NUMBER:
      return unpack('>d', self.read_bytes(8))[0]
    # elif type == TYPE_BOOLEAN:
    #   return unpack('>?', self.read_bytes(1))

    elif type == TYPE_STRING:
      size = unpack('>H', self.read_bytes(2))[0]
      return self.read_bytes(size).decode('utf-8')
    # elif type == TYPE_NULL:
    #   return None
    # elif type == TYPE_UNDEF:
    #   return None # Technically a separate type. But who cares.
    # elif type == TYPE_REF: # Denoted MixedArray by pyamf
    #   pass

    elif type == TYPE_EARRAY: # Dynamic array
      size = unpack('>I', self.read_bytes(4))[0]
      data = []
      for _ in range(size):
        self.i += 3 # I'm not sure whose fault it is, but there seem to be 3 extra bytes here.
        data.append(self.amf0_read())
      return tuple(data)

    else:
      raise ValueError(f'Cannot read type: {type}')

  def amf0_write(self, data):

    if isinstance(data, int) or isinstance(data, float):
      self.i += 1 # Skip over the type info in the old structure
      self.write_bytes(pack('>d', data))

    elif isinstance(data, str):
      self.i += 1 # Skip over the type info in the old structure
      old_size = unpack('>H', self.read_bytes(2))[0]
      if len(data) > old_size:
        raise ValueError('Cannot write more data')
      data += '\0' * (old_size - len(data)) # Pad with NUL
      self.write_bytes(data.encode('utf-8'))

    elif isinstance(data, list) or isinstance(data, tuple):
      pos = self.i
      old_data = self.amf0_read()
      self.i = pos
      if len(data) > len(old_data):
        raise ValueError('Cannot write more data')
      data += old_data[len(data):]
      self.i += 5 # Skip over old type data + array length
      for d in data:
        self.i += 3 # Skip over 3 garbage bytes
        self.amf0_write(d)

    else:
      raise ValueError(f'Cannot write type: {type(data)}')

"""
70 6C 61 79 74 69 6D 65 # playtime
08 # ECMA Array Type
00 00 00 03 # LE array size?
00 01 30 00
00 00 00 00 00 00 00 00 # 0 (double)
00 01 31 00
3F F0 00 00 00 00 00 00 # 1 (double)
00 01 32 00
40 4B 80 00 00 00 00 00 # 55 (double)
"""