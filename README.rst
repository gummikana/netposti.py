netposti.py
===========

netposti.py is a small python script that forwards your mails from NetPosti.fi
to your email address.

NetPosti.fi is a Finnish Post Office / Itella service that scans your physical
mail and stores it at NetPosti.fi as PDF files. Unfortunately they don't 
allow users to forward these PDF files to their email addresses, but force
them to use their NetPosti.fi service. 

So I created a small script that does that for you. Some tweaking may be 
required, the code isn't perfect. But it does the job.


How to use this
---------------

 IMPORTANT: I'm not responsible for anything this script does. 

 1. You need to setup an username with NetPosti at http://www.netposti.fi/
     Once you have those, fill them in to the script

 2. You may need a gmail account, for sending the attachments
	If you wanna use gmail to send your mail fill in your gmail data 
	underneat
	If you don't want to use gmail, modify the send_mail function to
	send mail without gmail. Shouldn't be too hard to do.

 3.  Run the script.

 (The way it's setup now is that it will only email you the new mails, 
  you might want to change that for debugging/testing purposes)

 Also you might want to modify the email content part. 



License
-------

netposti.py is provided under the MIT license

