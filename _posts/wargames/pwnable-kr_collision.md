---
title: "pwnable.kr: bof [no-markdown]"
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

Picking up where we left on the pwnable.kr grind, we continue onto the next pwnable problem labeled ‘collision.’ 

![pwnable-kr_collision/pwnable-kr_collision_1.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_1.jpg)

The hint states: “Daddy told me about cool MD5 hash collision today. I wanna do something like that too!” This is going to be a problem about hashing, a concept fundamental in encryption. Hashing essentially allows us to take text into a function H and output a convoluted cipher c, void of meaning. Thus H(t) = c, taking the inverse with c will allow you to get the original text. To make reversing this process harder we usually add a random constant string S called a salt. Therefore H(t + S) = c is a much harder function to reverse. Because H is not a bijection, there exists a c = H(t1 + S) = H(t2 + S), where t1 and t2 are different strings.

To simplify the ridiculous show-offiy math above, we are looking for two words we put into the program that will have the same output. This can be said before we even look at the innards of the program. Now that we are done flexing out math skill, lets get into the actual program. 

We are provided the necessary login credentials for an ssh server again on col@pwnable.kr through port 2222. This should be a similar attack vector as the last problem, if you don’t know how to use ssh yet check out the last post. We check the contents of our working directory, along with its permissions to see what we got. 

![pwnable-kr_collision/pwnable-kr_collision_2.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_2.jpg)

As usual, we cannot just read the flag, else all the fun would be lost, because our permissions are limited. My hacker senses tell me that we are going to ‘cat’ the flag from exploiting the col program. Lets run the program and see what happens. 

![pwnable-kr_collision/pwnable-kr_collision_3.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_3.jpg)

It appears on face value that this program limits how much input we can put into the program, sadly no buffer overflow… It also appears that we must put exactly 20 bytes of input into the program. Because characters are 1 byte large, that means we must always enter 20 characters. Now it’s time to crack this bad boy open. Lets open the program with a ‘cat’ command. 

![pwnable-kr_collision/pwnable-kr_collision_4.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_4.jpg)

This program has some tricky things going on. It’s checking to see if we enter the needed amount of bytes, then it is checking the quality of the entered bytes against ‘hashcode’ which we know the value of, its at the top of the code. So really thats the most important thing, whatever goes into the checkpassword() function needs to equal ‘hashcode’ for us to get the flag. So lets reduce the code we need to look at. As I’ve been told, knowing what to skip is essential to hacking. 


![pwnable-kr_collision/pwnable-kr_collision_5.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_5.jpg)

Now, we need to understand this functions process. Something is going on here with pointers, so a quick pointer brief is warranted. Notice the first process that is done is a character pointer being casted and set to a integer pointer. Because characters are one byte large, we incremented below we would move one CHARACTER up… but we do not input ‘characters’ into this program. We need to input characters that equal the hex value of  0x21DD09EC, which means we need to enter hex bytes. Recall, one hex value, which is an integer, is four bytes large. Therefore, the loop below increments through 5 hex values essentially grabbing all 20 hex bytes we enter. So really, we need to enter 5 hex values of the order 0xcafebabe, that was a cheeky example.


![pwnable-kr_collision/pwnable-kr_collision_6.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_6.jpg)

So lets take a deep breath and analyze all the data presented. The way we get our flag is by getting this function, the loop above, to equal ‘hashcode’ which equals 0x21DD09EC. We need to input 20 individual hex bytes, that will be read in 5 hex values like 0xcafebabe. So really, we just need to input ((0x21dd09ec)/5) five times because it will add up those bytes in this for loop that goes through 5 hex values. Thus we need to do some QUICK MATHS. We can use python for that by calling ‘python’ in our terminal 

![pwnable-kr_collision/pwnable-kr_collision_7.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_7.jpg)

Then we just type our math as seen. We use the built-in hex() function from python. This will just print our math out in hex notation so it looks nice to us, its not required, but highly recommended. As a sanity check multiply our end result by 5 to be assured it adds up to 0x21dd09ec. Good thing we checked, because 0x21dd09e8 is not  0x21dd09ec, I know they look really similar. So we can just subtract the difference and we should get the remainder. We add the remainder to any of the five 0x6c5cec8 we got earlier, than we should be home free.

As a recap we need to input  0x6c5cec8 four times, and 0x6c5cecc once. So we could write out  0x6c5cec8 four times… or we could get fancy with some python, trust me it is hella useful later. We input our miniature python script into our program like we do any other input, after the ./col. The only difference is we use the $ character before calling a python to indicate we want the value of the expression and not the literal expression as input. So lets finish this! All we have to do is input or data. We indicate a hex byte with a little \x before our value like \xca is 0xca.


![pwnable-kr_collision/pwnable-kr_collision_8.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_8.jpg)

Well that was disappointing. Really thought I had it there. OH WAIT, we need to remember one tiny little fact about the system we are playing on… its x86 32bit… what does that even mean? Well it is a little to much to explain in one post, so go search up what it means. All that matters is that it means this system is in little endian. Little endian means every byte we enter is backwards… don’t ask why, it’s just one of those things we never got to fixing in computers. Just kidding totally ask why and investigate and report here. I would love to know more. 

Back to business. All we have to do is flip the order in which we entered the bytes. That easy, lol. 


![pwnable-kr_collision/pwnable-kr_collision_9.jpg](/assets/images/wargames/pwnable-kr_collision/pwnable-kr_collision_9.jpg)

mahaloz.

Flag: ‘daddy! I just managed to create a hash collision :)’
-mahaloz
