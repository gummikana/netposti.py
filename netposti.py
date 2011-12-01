#**************************************************************************
#  
#  Copyright (c) 2011 Petri Purho
# 
#  This software is provided 'as-is', without any express or implied
#  warranty.  In no event will the authors be held liable for any damages
#  arising from the use of this software.
#  Permission is granted to anyone to use this software for any purpose,
#  including commercial applications, and to alter it and redistribute it
#  freely, subject to the following restrictions:
#  1. The origin of this software must not be misrepresented; you must not
#     claim that you wrote the original software. If you use this software
#     in a product, an acknowledgment in the product documentation would be
#     appreciated but is not required.
#  2. Altered source versions must be plainly marked as such, and must not be
#     misrepresented as being the original software.
#  3. This notice may not be removed or altered from any source distribution.
#
#**************************************************************************/

# How to use this
# IMPORTANT: I'm not responsible for anything this script does. 
#
# 1. You need to setup an username with NetPosti at http://www.netposti.fi/
#     Once you have those, fill them in to the script
#
# 2. You may need a gmail account, for sending the attachments
#	If you wanna use gmail to send your mail fill in your gmail data 
#	underneat
#	If you don't want to use gmail, modify the send_mail function to
#	send mail without gmail. Shouldn't be too hard to do.
#
# 3. Run the script.
#
# (The way it's setup now is that it will only email you the new mails, 
#  you might want to change that for debugging/testing purposes)
#
# ---- 
# Also you might want to modify the email content part. 
#

import mechanize
import cookielib

NETPOSTI_USERNAME = "YOUR_NETPOSTI_USERNAME"
NETPOSTI_PASSWORD = "YOUR_NETPOSTI_PASSWORD"
NETPOSTI_DEBUG = False
NETPOSTI_TO_EMAIL = ["YOUR_EMAIL@ADDRESS.COM"]

GMAIL_FROMADDR = "SENDING_GMAIL_ADDRESS@GMAIL.COM"
GMAIL_LOGIN    = GMAIL_FROMADDR
GMAIL_PASSWORD = "YOUR_GMAIL_PASSWORD"


#------------------------------------------------------------------------------
# <send_mail>
import smtplib
import os
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders

def send_mail(send_to, subject, text, files=[]):
	assert type(send_to)==list
	assert type(files)==list

	msg = MIMEMultipart()
	msg['From'] = GMAIL_FROMADDR
	msg['To'] = COMMASPACE.join(send_to)
	msg['Date'] = formatdate(localtime=True)
	msg['Subject'] = subject

	msg.attach( MIMEText(text) )

	for f in files:
		part = MIMEBase('application', "octet-stream")
		part.set_payload( open(f,"rb").read() )
		Encoders.encode_base64(part)
		part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
		msg.attach(part)

	# smtp = smtplib.SMTP(server)
	server = smtplib.SMTP('smtp.gmail.com', 587)
	# server.set_debuglevel(1)
	server.ehlo()
	server.starttls()
	server.login(GMAIL_LOGIN, GMAIL_PASSWORD)
	server.sendmail(GMAIL_FROMADDR, send_to, msg.as_string())
	server.quit()

#------------------------------------------------------------------------------
  
  
# Browser
br = mechanize.Browser()

# Cookie Jar
cj = cookielib.LWPCookieJar()
br.set_cookiejar(cj)

# Browser options
br.set_handle_equiv(True)
br.set_handle_gzip(True)
br.set_handle_redirect(True)
br.set_handle_referer(True)
br.set_handle_robots(False)

# Follows refresh 0 but not hangs on refresh > 0
br.set_handle_refresh(mechanize._http.HTTPRefreshProcessor(), max_time=1)

# User-Agent (this is cheating, ok?)
br.addheaders = [('User-agent', 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.1) Gecko/2008071615 Fedora/3.0.1-1.fc9 Firefox/3.0.1')]

#"""
# -----------------------------------------------------------------------------
# <LOGIN>
# Open some site, let's pick a random one, the first that pops in mind:
r = br.open('http://netposti.fi')

# Select the first (index zero) form
br.select_form(nr=0)

# Let's login
br.form['login.username']=NETPOSTI_USERNAME
br.form['login.password']=NETPOSTI_PASSWORD
br.submit()

# </LOGIN>
# -----------------------------------------------------------------------------
# <PARSING>

main_page_url = br.geturl();

# while message-item unread is found, we go through all the links and send their contents
# check if there are new messages to be parsed...
if ( NETPOSTI_DEBUG == False | br.response().read().find('message-item unread') < 0 ):
	exit()

linklist = []
for link in br.links(url_regex="openMessage::ILinkListener::"):
	linklist.append(link.url)
# </PARSING>

i = 0

while( br.response().read().find('message-item unread') > 0 ):
	# we should probably parse these links so that they are saved to a file
	# and the new ones are opened and pdfed
		
	#"""
	# -----------------------------------------------------------------------------
	# <OPEN THE FIRST MAIL LINK>
	r = br.open( linklist[i] )
	base_url = br.geturl()
	base_url = base_url[0:base_url.find('?')]

	# hackish parsing of data
	html_data = r.read()

	# Parse sender
	# <span class="sender">ITELLA/VIESTINV?LITYSPALVELUT</span>
	parse_prefix = '<span class="sender">'
	start_pos = html_data.find( parse_prefix )
	assert( start_pos > 0 )

	end_pos = html_data.find('</span>', start_pos)
	assert( end_pos > 0 )

	data_sender = html_data[start_pos + len(parse_prefix):end_pos]
	print data_sender

	# Parse subject
	br.select_form(nr=0)
	data_subject = br.form['messageSubjectTextField']


	# Parse PDF download link
	start_pos = html_data.find('class="small-pdf-icon"')
	assert( start_pos > 0 )

	end_pos = html_data.find('>', start_pos)
	assert( end_pos > 0 )
	assert( end_pos > start_pos )

	parse_part = html_data[start_pos:end_pos]

	parse_prefix = "window.location.href='"
	parse_postfix = "'"

	start_pos = parse_part.find( parse_prefix ) 
	assert( start_pos > 0 )

	start_pos += len(parse_prefix)
	end_pos = parse_part.find( parse_postfix, start_pos )
	assert( end_pos > 0 )

	pdf_download_url = parse_part[start_pos:end_pos]
	print parse_part[start_pos:end_pos]

	downloaded_pdf_file = br.retrieve(base_url + pdf_download_url)[0]
	if ( downloaded_pdf_file[-4:] != 'pdf' ):
		os.rename(downloaded_pdf_file, downloaded_pdf_file + '.pdf')
		downloaded_pdf_file += '.pdf'

	print downloaded_pdf_file

	# ------------------------
	# Create the email

	email_subject = "Postia - " + data_sender + ": " + data_subject
	email_content = "Kusti toi oikeeta postia:\nLahettaja: " + data_sender + "\nOtsikko: " + data_subject + "\n\nLoggaa sisaan http://netposti.fi/\n\n-KustiBot\n"

	send_mail( NETPOSTI_TO_EMAIL, email_subject, email_content, [downloaded_pdf_file]);

	#------

	r = br.open( main_page_url )
	i += 1

