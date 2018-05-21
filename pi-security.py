# frankencode with ideas and snippets adapted from many sources including here:
# https://www.raspberrypi.org/forums/viewtopic.php?t=86441&f=32

import time
import RPi.GPIO as GPIO
from subprocess import call
import string
import smtplib
# For guessing MIME type
import mimetypes 
# Import the email modules we'll need
import email
import email.mime.application 
#Import sys to deal with command line arguments
import sys
from subprocess import call  

GPIO.setwarnings (False)
# using BCM not BOARD here, else pin 7 should be 26
GPIO.setmode(GPIO.BCM)
time_stamp = time.time() #for debouncing

#set pins
#pin 7 = motion sensor 1, pin 8 = motion sensor 2, pin 14 = dummy
GPIO.setup (7, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup (8, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
GPIO.setup (14, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

counter = 1

def take_pic(sensor):	
	global counter
	call(["raspistill -vf -hf -o image" + sensor + str(counter) + ".jpg"], shell=True)
#	time.sleep(2) #wait 2 seconds before continuing
	call(["raspivid -w 1024 -h 576 -fps 60 -t 20000 -o vid" + sensor + str(counter) + ".h264"], shell=True)
#	time.sleep(35) #wait 35 seconds before continuing
	

def drop_box(sensor):	
	global counter
	photofile = "/path/to/dropbox_uploader.sh upload /path/to/vids" + sensor + str(counter) + ".h264 vid" + sensor + str(counter) + ".h264"
	call ([photofile], shell=True)
#	time.sleep(35) #wait 35 seconds before continuing


def send_text(details):
	# Create a text/plain message
	msg = email.mime.Multipart.MIMEMultipart()
	msg['Subject'] = 'Security Alert'
	msg['From'] = 'any@email.address'
	msg['To'] = 'to@email.address'

 
	# The main body is just another attachment
	body = email.mime.Text.MIMEText("""body text here""")
	msg.attach(body)
 
	# use jpg not pdf
 
	#directory=sys.argv[1]
	directory = 'imagemotion' + str(counter) + '.jpg'
 
	# Split directory into fields separated by / to subtract filename
 
	spl_dir=directory.split('/')
 
	# We attach the name of the file to filename by taking the last
	# position of the fragmented string, which is, indeed, the name
	# of the file we've selected
 
	filename=spl_dir[len(spl_dir)-1]
 
	# We'll do the same but this time to extract the file format (pdf, epub, docx...)
 
	spl_type=directory.split('.')
 
	type=spl_type[len(spl_type)-1]
 
	fp=open(directory,'rb')
	att = email.mime.application.MIMEApplication(fp.read(),_subtype=type)
	fp.close()
	att.add_header('Content-Disposition','attachment',filename=filename)
	msg.attach(att)
 
	# send via Gmail server
	s = smtplib.SMTP('smtp.gmail.com:587')
	s.starttls()
	s.login('to@email.address','password')
	s.sendmail('any.email.address','to@email.address', msg.as_string())
	s.quit()


def motion_callback(channel):
    global time_stamp
    global counter
    time_now = time.time()
    if (time_now - time_stamp) >= 0.3: #check for debouncing
	print "Motion detector detected GPIO 7 " + str(counter)
	take_pic("motion")
#	time.sleep(5) #wait 5 second for pic to show up in dir before trying to attach
	drop_box("motion")
	send_text("Motion detector")
	counter +=1   
	time_stamp = time_now
	
def motion_callback2(channel):
    global time_stamp
    global counter
    time_now = time.time()
    if (time_now - time_stamp) >= 0.3: #check for debouncing
	print "Motion detector detected GPIO 8 " + str(counter)
	take_pic("motion")
#	time.sleep(5) #wait 5 second for pic to show up in dir before trying to attach
	drop_box("motion")
	send_text("Motion detector")
	counter +=1   
	time_stamp = time_now

#main body
raw_input("Press enter to start program\n")

GPIO.add_event_detect(7, GPIO.RISING, callback=motion_callback)
GPIO.add_event_detect(8, GPIO.RISING, callback=motion_callback2)


# pressure switch ends the program
# you could easily add a unique callback for the pressure switch
# and add another switch just to turn off the network
try:
    print "Waiting for sensors..."
    GPIO.wait_for_edge(14, GPIO.RISING)
except KeyboardInterrupt:
    GPIO.cleanup()

GPIO.cleanup()