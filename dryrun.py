#!/usr/bin/python

''' 
dryrun.py: This program is a humble attempt to decouple the process part of 
the "Input, process, output" cycle by presenting an interface which doesn't require
having the compilers/locally installed or remotely logging to your  development computer.
Its a proof-of-concept now, a personal curiosity really.

NB: This code is not to be invoked on its own, for the proper functioning. Please 
see README.

Amit Saha < droidery@gmail.com> 
http://echorand.me
Version PoC: 27 August, 2011

'''


from string import Template
import subprocess

import poplib
import smtplib
import imaplib
import mimetypes
import email
from email.parser import Parser
from email.parser import HeaderParser
from email import encoders
from email.message import Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import logging


# Global configs for the mailbox which acts
# as the receiever for code execution requestions
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
IMAP_SERVER = 'imap.gmail.com'
username = 'your username'
password = 'your password'

#dictionary for code_language->extension

extensions = {'c':'c',
              'cpp':'cxx',
              'latex':'tex',
              'python':'py'
              }

#program for processing the file
programs ={'c':'gcc',
           'cpp':'g++',
           'latex':'pdflatex',
           'python':'python'
           }


# IMAP access to get the code
# code built upon 
# http://bitsofpy.blogspot.com/2010/05/python-and-gmail-with-imap.html
# and http://segfault.in/2010/08/playing-with-python-and-gmail-part-2/
def imap_access(username,password):

    imap_server=imaplib.IMAP4_SSL(IMAP_SERVER)
    imap_server.login(username,password)
    
    # select INBOX
    imap_server.select('INBOX')
    
    # Search for all new emails in INBOX
    status, email_ids = imap_server.search(None, '(UNSEEN)')
    
    # placeholders
    senders=[]
    code_languages=[]
    codes=[]

    # Retrieve Sender, Subject, code for each new request
    if email_ids != ['']:
        for e_id in email_ids[0].split():

            # Extract sender, code language
            response,data = imap_server.fetch(e_id, '(RFC822)')

            # parse response to extract sender,code_language,code
            header_data = data[0][1]
            parser=HeaderParser()
            msg = parser.parsestr(header_data)

            sender = msg['From']
            code_language= msg['Subject']


            # extract code from the body

            # assuming that the message is single part
            # the code resides in the body of the message

            code =  email.message_from_string(data[0][1])
            code = code.get_payload()
            
            senders.append(sender)
            code_languages.append(code_language)
            codes.append(code)

    # logout
    imap_server.logout()

    return senders,code_languages,codes

# Get input
def get_code():
    
    senders,code_languages,codes = imap_access(username,password)
    return senders,code_languages,codes

# Process
def execute_code(code_language,code):
    
    #first create a source file from the code
    #to help in compilation/execution

    fname_template = Template('code.$ext')
    #TODO: error checking
    fname=fname_template.substitute(ext=extensions[code_language])
    f = open(fname,'w');
    f.write(code);
    f.write('\n');
    f.close()

    #now process the file

    # for C/C++ programs, its a two step process:
    # 1. compile
    # 2. If successful, execute a.out and send the output

    # for Python programs
    # python code.py, the output/error can be directly sent as reply

    # for LaTex
    # compile the LaTex file and send the PDF output back
    # will need MIME handling and send PDF as an attachment

    # get the appropriate processor
    # TODO: error checking
    program=programs[code_language]

    # process
    subprocess_args = [program,fname]

    # Write the process log to a file
    # send as an attachment in the reply
    f=open('process.log','w')
    f.write('Output produced during processing of your file\n')

    # http://docs.python.org/library/subprocess.html#subprocess.check_output
    subprocess_retcode = 0;
    try:
        subprocess_output=subprocess.check_output(subprocess_args,stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as error:
        subprocess_retcode = error.returncode
        # Write the error message to the file
        f.write(error.output)
        f.write('\n')

    # if the processing was succesful, write the command output
    # to the log
    if subprocess_retcode == 0:
        f.write(subprocess_output)
        f.write('\n')

        #for C/C++ code, the next step
        if code_language == 'c' or code_language == 'cpp':
            subprocess_retcode = 0;
            try:
                subprocess_args = ['./a.out']
                subprocess_output=subprocess.check_output(subprocess_args,stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as error:
                subprocess_retcode = error.returncode
                # Write the error message to the file
                f.write(error.output)
                f.write('\n')

            #write the output to the file
            if subprocess_retcode == 0:
                f.write(subprocess_output)
                f.write('\n')
    
    #close log file
    f.close()

#Create an email message for sending the output
# Built upon code from http://docs.python.org/library/email-examples.html
def send_output(sender,code_language):
    # create output message
    # Send the process.log alongwith any other files generated
    # for example, LaTex would generate a PDF file, called 'code.pdf' 
    # in this case
    outer = MIMEMultipart()
    outer['Subject'] = 'Output of your code'
    outer['To'] = sender
    outer['From'] = 'ICANHAZOUTPUT'

    # atach the process.log file
    # this is for all languages
    fp = open('process.log')
    msg = MIMEText(fp.read(), _subtype='text')
    fp.close()
    msg.add_header('Content-Disposition', 'attachment', filename='process.log') 
    outer.attach(msg) 
    
    # special cases

    # LaTex will produce a PDF - code.pdf
    # attach it
    
    if code_language=='latex':
        ctype, encoding = mimetypes.guess_type('code.pdf')
        maintype, subtype = ctype.split('/', 1)

        fp = open('code.pdf','r')
        msg = MIMEBase(maintype,_subtype=subtype)
        msg.set_payload(fp.read())
        fp.close()

        msg.add_header('Content-Disposition', 'attachment', filename='code.pdf') 
        outer.attach(msg) 
        
    # send the message
    reply = outer.as_string()
    session = smtplib.SMTP(SMTP_SERVER,SMTP_PORT)
    
    session.ehlo()
    session.starttls()
    session.ehlo
    session.login(username, password)
    session.sendmail('ICANHAZOUTPUT', sender, reply)
    
    session.quit()

# Entry point
def dryrun_invoke():

    #input
    senders,code_languages, codes = get_code()
    
    if senders==[]:
        return


    for i in range(len(senders)):
        request_template = Template('Processing request from $sendr $code_lang')
        request = request_template.substitute(sendr= senders[i],code_lang=code_languages[i])
    
        logging.info(request)

    #process
        if code_languages[i] in extensions:
            execute_code(code_languages[i],codes[i])
        else:
            f=open('process.log','w')
            f.write('This programming language is currently not supported\n')
            f.close()

        #output
        send_output(senders[i],code_languages[i])
