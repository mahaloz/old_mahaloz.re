---
title: "pwnable.kr: bof writeup"
tags:
  - table of contents
toc: true
category:
  - wargames
---
This challenge is centered around two downloadable files: [bof](http://pwnable.kr/bin/bof) and [bof](http://pwnable.kr/bin/bof.c). With a netcat connection of `pwnable.kr` on port 9000. The hint states: `Nana told me that buffer overflow is one of the most common software vulnerability. Is that true?`


*NOTE TO READER*: I wrote this writeup before I started writing using MarkDown
(yeah that was a long time ago). In the case that anything is inaccurate, sorry.
Also the code on this post is a picture. So sorry again :p. There should only be
around 5 of these.

Continuing down the road to bro hacker we come across our next pwning problem: bof. From what I’ve learned in basic programming classes for C programming, if you don’t know C, I highly suggest learning it, bof probably is short for buffer overflow—the oldest hack in the book. Buffer overflows concept can be simplified to a simple pond analogy. Imagine you have two ponds in succession.

![pwnable-kr_bof/pwnable-kr_bof_ponds.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_ponds.jpg) 

The ponds are filled with water. Each pond has a limited and finite set of space for the water to fill. Once the water fills the space of the pond it starts overflowing into the other pond. Remember, that since new water is entering the lower pond, then the current water of the pond will go to the bottom of the pond because new water is surfacing the top. 

The ponds are computer registers. The water is passed in data, or input. When we allocate space for an array, also known as a buffer, we allocate a set amount of space in memory. When we input too much data into the buffer, it has to go somewhere… it goes to the lower registers, or things below it. So if we have one buffer allocated with 60 bytes, arr1[60], and a second array allocated with 20 bytes, arr2[20], then inputting 70 bytes into arr1 will fill arr2 with 10 bytes if arr2 is below arr1 in memory. Now that we have the idea figured out, lets jump into this problem.

This time around we do not have an ssh login, so it looks like we will be doing the majority of our hacking locally and then finishing up with with ‘netcat,’ I’ll explain that later. We can use the command line to download the following links using `wget` command. Yes I know its the same image as above!

![pwnable-kr_bof/pwnable-kr_bof_1.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_1.png) 

Just like before, lets try run the program before we actually dive into its code, though it is obvious that the flag we want to exploit is not stored on my computer. We do this just to see what the program responds too. Sadly I get an error from bash.


![pwnable-kr_bof/pwnable-kr_bof_2.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_2.png) 

After some googling, I realized I am running a 64 bit operating system, but the binary is 32 bit. This can cause problems when using libraries and such. We can see that this file is 32 bit by using the ‘file’ command. 

![pwnable-kr_bof/pwnable-kr_bof_3.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_3.png) 

We can install the necessary libraries using apt-get.

![pwnable-kr_bof/pwnable-kr_bof_4.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_4.png)

Ok now we should be ready to go. Lol. Lets try this again. We run the program with some normalish looking input, and then some really long input, it is a buffer overflow after all. Something interesting happens this time when we run it with large input.


![pwnable-kr_bof/pwnable-kr_bof_5.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_5.png) 

For one we get a message from the terminal saying we are smashing a stack, a.k.a. performing a buffer overflow. So the computer knows we are being not nice with this binary. On top of that we got something aborted a dumped. This is important for later because data is literally dumped out of this program, which we can do manually. Now that we have confirmed that a buffer overflow exists, lets pop the hood of this bad boy. I like to use vim.

![pwnable-kr_bof/pwnable-kr_bof_6.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_6.png) 

Now that we are pros at reading code, I will try to zoom through the analysis of this code. Main calls func() with an input of 0xdeadbeef. That is stored in the function as key. We then give input to func() through the gets command, which is put in a 32 byte buffer. Then key is checked against 0xcafebabe, if it is true we get a shell. The shell will allow us to manually ‘cat’ the flag. 

Now you are probably asking yourself, “how the hell do we change key, if our input never goes to key?” Well it is a buffer overflow problem… To understand how we can take advantage of overflowing one space of memory, we need to take it back to the basics of programming in a compiled language. When C code is compiled, the C code is translated into machine code—a code of mnemonics and operations. The machine code is layed out in memory on a Stack data structure. We can view the machine code of any compiled program by disassembling it. Luck for us, we got a free one built into linux: objdump. 

We can dump the machine code of the bof program to better understand how the program looks in memory. Recall, that the compiler can do things the user does not specify when compiling a program, like completely removing a segment of loops, or allocating more memory. Using the ‘man’ page of objdump, we can understand the flags we need to pass it to disassemble. I like reading disassembly in Intel and thus I pass the -M Intel option. 


![pwnable-kr_bof/pwnable-kr_bof_7.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_7.png) 

I shortened the image above, because the output is so large. Don’t get overwhelmed. A big part about being a good hacker is knowing what’s not important. The only piece of code that is really important is the func() function. Luckily, function names are preserved in disassembly, so lets pipe this crazy big input into a word processor like ‘less’ and search for “func.”


![pwnable-kr_bof/pwnable-kr_bof_8.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_8.png) 

Now we search with the ‘/’ in less, and we search for “func.” We will get the dissasembly of that function.

![pwnable-kr_bof/pwnable-kr_bof_9.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_9.png) 

This is where things start getting interesting. Understanding machine code can be hard at times because of the endless jmps that occur. The calling convention used for this machine code is x86—knowing what each instructions does is crucial to understanding the code. A reference for x86 can be found here. 
Notice some things are easily readable, like the familiar 0xcafebabe on the far right column, guess what operation that one is? Without a great knowledge of x86 we can start piecing together what is what from the C code. Notice the cmp instruction? That is our if statement. Let’s plow through this code section, by section.

The first three lines are called the prologue. The esp is moved into the ebp position. Space is made by subtracting from the esp. In this instance 0x48 is subtracted, thus 0x48 is the space allocated for this function. 

![pwnable-kr_bof/pwnable-kr_bof_10.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_10.png) 

Next we have some values being passed and space being allocated to eax. The value 0x14 is copied into eax, then eax is copied, the procedure of mov, into ebp-0xc. This is important because this within our earlier allocation of 0x48. Lastly, eax is set to zero with a cheeky optimization of eax xoring eax. 


![pwnable-kr_bof/pwnable-kr_bof_11.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_11.png) 

Just to demonstrate the hacker mindset, everything we discussed earlier is actually irrelevant to the problem, but helpful to know in the long run. There is only two things important to us, the address of key and the address of overflowme. If we get those we can overflow the overflowme buffer with as much data we need to reach key. So really only the next few lines matter, and out of those, only two lines matter.

![pwnable-kr_bof/pwnable-kr_bof_12.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_12.png) 

We know the location of key because key is going to be compared to 0xcafebabe. The location must be ebp+0x8. We only have the conformation that it is an offset of ebp, the place local variables are stored.


![pwnable-kr_bof/pwnable-kr_bof_13.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_13.png) 

We know the location of overflowme is ebp-0x2c because of three things: 1. It’s the only memory space bigger than 32 bytes here, 2. It comes right after the puts function, 3. Something is moved from the location that is a DWORD PTR, also known as a string… hmmm. Yeah. 

![pwnable-kr_bof/pwnable-kr_bof_14.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_14.png) 

Now, we are coming down to the final parts. We just need to figure out how far key is from overflowme. We got the addresses, so, displacement = (ebp-0x2c) – (ebp+0x8). The address of ebp is the start of func(), thus it is 0x0000062c. Lets python this math out.


![pwnable-kr_bof/pwnable-kr_bof_15.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_15.png) 

The displacement is 52 bytes. So we need to fill out input with 52 bytes, then give the value we want to over right key. So 52 A’s and our 0xcafebabe should work… We can use python and little endian syntax as we did in the last writeup. Finally we need to pipe our output into the pwnable.kr Netcat.

Netcat can be approached like any other program, thus a pipe in works like anything else. So we just pipe our payload to nc pwnable.kr 9000.


![pwnable-kr_bof/pwnable-kr_bof_16.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_16.png) 

OMG we are so close. But we still failed. We are forgetting one tiny thing… how the heck are we going to use our shell if we have not exited our program? We can’t… thats the whole point of using bash. What we need to do is find a way to return us to the stdin which is in bash. After some google searching, there is a cool way to do this. We can append a ‘cat -’ to the end of our python command so it cats nothing really, but puts us in the shell. Once there, we can cat flag. LETS DO THIS.


![pwnable-kr_bof/pwnable-kr_bof_17.png](/assets/images/wargames/pwnable-kr_bof/pwnable-kr_bof_17.png) 

mahaloz.

Flag: daddy, I just pwned a buFFer :)








	








