import interact
import struct

# Pack integer 'n' into a 8-Byte representation
def p64(n):
    return struct.pack('Q', n)

# Unpack 8-Byte-long string 's' into a Python integer
def u64(s):
    return struct.unpack('Q', s)[0]

p = interact.Process()
# data = p.readuntil('\n')
p.sendline("\nw w w w w w w w \n\nw w w w w w w \n\nw w w w w w w w \n\nw w w w w w w w \n\ncaaaaaadw w w w w w w w w \n\nw w w w w w w w\n\naaaaaadd dwd caaaad aaddda daadwd dddd aaddw aaa ddaacd aadcaaw d awa daaw aw  awa daa dad aaawd w w w \n\naaaaaadd dwd dddd aaa  aacddddd dddddaaa aaacw  aaa awa awa wdd daaawww dw waa awaaaa caaaaaawa ddddd  w w w\n")

p.interactive()
