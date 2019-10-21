---
title: "pwnable.kr: passcode writeup"
tags:
  - table of contents
toc: true
category:
  - wargames
---


Back at the hack game again, lets go. This time around we are provided an ssh login again for  `passcode@pwnable.kr -p2222` with password `guest`. The hint also states: “Mommy told me to make a passcode based login system. My initial C code was compiled without any error! Well, there was some compiler warning, but who cares about that?” 
					
*NOTE TO READER*: I wrote this writeup before I started writing using MarkDown
(yeah that was a long time ago). In the case that anything is inaccurate, sorry.
Also the code on this post is a picture. So sorry again :p. There should only be
around 5 of these.

Just from the hint, we probably are going to want to compile whatever code we get so we can see the warning for ourselves. First lets run the program with some input as usual.

![pwnable-kr_passcode_1.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_1.png)

It’s hard to tell that the input is doing something strange, so lets just jump into the C code.


![pwnable-kr_passcode_2.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_2.png)

Looking at the code, this should be a simple password verification system where we put in the passcodes as seen in the C code and we get our flag.


![pwnable-kr_passcode_2.1.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_2.1.png)

But that does not work for some reason, and even more interestingly the program has a Seg fault. A Seg Fault occurs when the program tries to access memory that is not allowed. I have a feeling that has something to do with the warnings in our compilation. 

Lets copy and compile the code ourselves so we can see the warnings.
	

![pwnable-kr_passcode_3.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_3.png)

We get two warnings, but of course it still compiles. Both errors have something to do with the type of passcode1 and passcode2. Both seem to be ints, but the program is expecting an integer pointer. This can cause problems, like writing on an address instead of in it, i.e. the values is not overwritten but the address gets overwritten. 

This is the reason our program has a Seg Fault. The program reads in an int that changes passcode1’s address. So when I entered 338150, that value was set as passcode’s address in memory… making this a very strange and powerful bug in this code. We have the power to change passcode1’s address to whatever we want.  

Now that we kinda know what exploitation vector we are looking for, lets jump back in the code. 


![pwnable-kr_passcode_2.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_2.png)

Following the control flow of the program, main passes to welcome, then to login. We only have three points to give input: name (in welcome), passcode1, passcode2 (both in login). This is our only attack vector. We can see from trying to enter into passcode1, we have no way to input into passcode2.

We can get a close look at the program by disassembling it in gdb, p.s. I set my disassembly flavor to intel for a nice format.


![pwnable-kr_passcode_4.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_4.png)

Like we knew earlier, the welcome function is called in main, but after puts. We know that welcome has our name buffer. But where is it? Well looking in the disassembly we can see the large space made for something bigger than 100bytes… that sounds like our buffer.

![pwnable-kr_passcode_5.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_5.png)

With that knowledge we know that the address of our name buffer is at rbp-0x70.  This is useful because we could possibly use this for a buffer overflowish attack. Understanding that we have the power to change passcode1’s address, why don’t we just change passcode1’s address to somewhere that has the value… or we could do something smarter. We could instead use our address writing powers to jump to the instruction that gives us the flag.

Stay with me on this. So what we can do with our bug of writing to an address is write the address of a function and then overwrite that function with the address of the system() call to give us our flag.

So we can use our input into our name buffer to overwrite the initial value of passcode1. So lets find passcode1 in memory.


![pwnable-kr_passcode_7.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_7.png)

passcode1 is at rbp-0x10. The displacement is abs([rbp-0x70] – [rbp-0x10]) = abs(0x10 – 0x70) =  96.
Therefore we need 96 bytes of garbage before we hit passcode1. So we got 4 bytes to work with… how fortunate. How long is an address (also int’s size)? 4 bytes. Perfect. 

Now what do we do with the 4 bytes? We input the address of a function we want to overwrite that occurs before the if statement with passcode1 and passcode2. I nominate we use the fflush() function, because who even uses fflush. We need to find the address of the function, which we can get from something called the Global Offset Table. 

We can use objdump to view the PLT, within the global offset table is contained in, to be technical we are not viewing the GOT, but instead viewing some of the address present in the GOT.


![pwnable-kr_passcode_8.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_8.png)

The address of fflush() is 0x0804a004. We need to put this address in passcode1, so we can overwrite it later. 

Now we only need one more thing: the address of the system call used to give us our flag, notice we do not want the address of the system function, but the address of the call. Looking back at the code we need to realize that we have to call the instruction immediately before system(), because that is our arguments for the system call, else we call system with no arguments.

The address can be seen clearly in the login disassembly as 0x080485e3.


![pwnable-kr_passcode_9.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_9.png)

Ok we have all the puzzle pieces collected, now lets just put them together. As a summary, we got to write 96 bytes of garbage into name so we can overwrite passcode1. We want to overwrite passcode1 because the scanf() formating error. From passcode we want to overwrite what we wrote so we can jump to the calling of our system call. The address of the overwrite function (fflush) is  0x0804a004, the address of instruction we want to jump too is 0x080485e3. Don’t forget about little endian and that this needs to be done on our ssh client.


![pwnable-kr_passcode_finish.png](/assets/images/wargames/pwnable-kr_passcode/pwnable-kr_passcode_finish.png)

Before I say my winner cheer, take note of the order we got output. We got the flag with the earlier print statement. Really cool stuff, shows you the power and difference in assembly v. C.

mahaloz.

Flag: Sorry mom.. I got confused about scanf usage :(

