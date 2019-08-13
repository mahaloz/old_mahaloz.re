---
title: "pwnable.kr: flag [no-markdown]"
tags:
  - table of contents
toc: true
category:
  - wargames
---

*NOTE TO READER*: I wrote this writeup before I started writing using MarkDown
(yeah that was a long time ago). In the case that anything is inaccurate, sorry.
Also the code on this post is a picture. So sorry again :p. There should only be
around 5 of these. - mahaloz

Similar to last problem, we are given a binary to download and exploit, but this time we don’t have any source code. The download can be found at http://pwnable.kr/bin/flag. The hint states: “Papa brought me a packed present! let's open it.” 

Lets try and run the program with some normal input, aAnd some really long input.

![pwnable-kr_flag_2.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_2.jpg)

Ok, from the preliminary testing it seems that input may not matter in this problem. The return message says something about malloc() and strcpy, which means that the our flag is stored in a pointer in memory. Because the string existed in the program, it may still be in their as a printable character. I learned a quick trick from some other security researchers, a command exists in linux for us to do this: strings. 

As logic once said, “I run it...”


![pwnable-kr_flag_3.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_3.jpg)

So it does not look like we got a flag… but we got some important info about this executable. The line that seems interesting is the ‘packaging’ line. WAIT, that was in our hint… I have a feeling that this is the way, so I’m going to follow it. This seems to be packaged with something called UPX. 


![pwnable-kr_flag_4.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_4.jpg)

It is confirmed to be a real software. We can go to their non-github page for a premade version of upx that we can download. I used: https://github.com/upx/upx/releases/download/v3.94/upx-3.94-amd64_linux.tar.xz.

Once downloaded we can see the general use of the program by just running it. 


![pwnable-kr_flag_5.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_5.jpg)

Alright, we want to decompress our program, so we used the -d option.


![pwnable-kr_flag_6.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_6.jpg)

Now that its unpacked, lets try disassemble our program. When we look at the main function we can see malloc used, then a object called flag copied somewhere.


![pwnable-kr_flag_7.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_7.jpg)

We need to see what is stored there… we can use GDB to get it. GDB is a super powerful tool that allows us to stop our program while its running and examine specific parts of the program… yeah its hacky.

![pwnable-kr_flag_8.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_8.jpg)

Now that we got our disassembly, we can visually see where we are in instructions in main. We can also see that 6 instructions later we have the flag copied into rdx. So if we do a single instruction jump seven times, then we can stop immediately after the flag is copied into rdx. After that we can simply examine whats in rdx. If you don’t know how to use gdb I highly recommend learning it!


![pwnable-kr_flag_9.jpg](/assets/images/wargames/pwnable-kr_flag/pwnable-kr_flag_9.jpg)

And there’s our flag.

mahaloz. 

Flag: "UPX...? sounds like a delivery service :)"


