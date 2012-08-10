Dryrun - decoupling the process and putting it out there

Amit Saha <droidery@gmail.com>
http://echorand.me
Version PoC: 27 August, 2011

Usage
------
clone the repository. You should have three .py files:
- dryrun.py
- dryrun_driver.py
- imaplib2.py

To start the service, please modify the username/password of your IMAP/SMTP servers
in dryrun_driver.py and dryrun.py and run:

$ python dryrun_driver.py


You have to keep this process alive for as long as you want your service to be available. To use 
a different Email service provider, please change the relevant variables in dryrun.py and dryrun_driver.py.

See the process.log for some logging info

Simple Usage scenario
--------------------
Compose an email:

<begin message>

To: <usernam@domain>
Subject: python
Body: 

#!/usr/bin/python
print "Hello World!"

<end of message>

Once you send the email, you should get back an email from the email address with an attachment
'process.log', which will contain the output of your code along with any errors/warnings. If
you send garbage, you will get garbage.

Currently Supported languages:

Language  Subject
--------  ------ 
C 	  c
C++	  cpp
Python	  python
latex	  latex

For adding a new language, see below


About the code
--------------
The core file is dryrun.py. As the name implies, dryrun_driver.py is a driver calling dryrun.py's dryrun_invoke() method 
when a new request was receieved.

Detailed Description:


User Interface
--------------

As of now, this presents an email based interface, which requires the user of this
service send the input in the form of an email to a designated email address,
denoted in "username" below in the following format:

To: username@domain
Subject: Programming language
Body: Code 

ATTACHMENTS not supported

Sample email:

To: icanhazoutput@gmail.com
Subject: python
Body: 

#!/usr/bin/python
print "Hello World!"

Once you send the email, you should get back an email from the email address with an attachment
'process.log', which will contain the output of your code along with any errors/warnings. If
you send garbage, you will get garbage.

Dependencies:

To run the code:
- Needs Python 2.7+


Currently this program suports C/C++, Python and LaTex, so it assumes the presence of 
gcc,g++, Python and LaTex compilers, namely pdflatex

Including your language
-----------------------

Its very simple to extend this to include a language of your choice of course. As of now,
you can directly modify the 'extensions' and 'program' dictionary. But you will have to manually
include the "logic" your particular language may need before you get the following output. For 
example:

- Python code execution is a one-step process
- C/C++ two step: gcc/g++ and then ./a.out
- LaTex produces PDF output, so it needs to be attached seperately along with process.log
..and such.

Fine print
-----------

- Absolutely no thought about the security implications

- No attempt at using Idiomatic Python, please make suggestions

- Uses code snippets from around blogs for IMAP, SMTP access, which
has been acknowledged

- Limited testing in all ways. Tested with only GMail's IMAP/SMTP severs