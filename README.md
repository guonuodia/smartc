# smartc
This is a script language interpreter with syntax similar to C language and some features of Python added.
This script language is mainly used for debugging embedded devices, and the communication interface can be a serial port or other interfaces such as the 7816 interface in the smart card field. It uses a half-duplex debugging method, sending one command and receiving one command.In the system_send function of the Interpreter class, the sending and receiving of commands can be defined.
The basic syntax of this scripting language is similar to C language, but with the following differences:
1. Variables only support unsigned integers, hexadecimal strings, and bool type, but variable types do not need to be declared. To distinguish unsigned integers from hexadecimal strings, the '#' symbol needs to be added before unsigned integers. To reference hexadecimal strings, you can use syntax similar to Python, such as a=1234abcd;print(a[:2]), which will print 1234. The keywords for bool type are 'true' or 'True', and 'False' or 'false', and it supports the empty type keyword 'None'.
2. Global variables are defined in the form of "variable=;", and local variables do not need to be defined.
3. Functions must be defined before use, and function definitions start with the 'def' keyword. Function parameter types also do not need to be declared.
