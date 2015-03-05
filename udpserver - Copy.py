#!/usr/bin/python

import socket
import sys
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker 
from datetime import datetime
import logging
import logging.handlers


Base = declarative_base()

#Setting up logging defaults
LOG_FILENAME = "/tmp/udpserver.log"
LOG_LEVEL = logging.DEBUG

logger = logging.getLogger(__name__)

#Giving the logger a unique name
logger.setLevel(LOG_LEVEL)

#Make a handler that writes to a file at midnight and keeping 3 days backup
handler = logging.handlers.TimedRotatingFileHandler(LOG_FILENAME, when="midnight", backupCount=3)
#Formatting each message
formatter = logging.Formatter('%(asctime)s %(levelname)-8s %(message)s')
#Attaching format to handler
handler.setFormatter(formatter)
#Attach the handler to the logger
logger.addHandler(handler)

"""Declaring the tables in the database
DB name : dreadger
Table name : dieselLevel
"""

class DieselLevel(Base):
	__tablename__ = 'dieselLevel'
	id = Column(Integer, primary_key=True)
	device = Column(String(25))
	level = Column(Integer)
	mTime = Column(DateTime)
	ip = Column(String(15))

	def __init__(self, device, level, mTime, ip):
		self.device = device
		self.level = level
		self.mTime = mTime
		self.ip = ip

"""Logging in as admin """
engine = create_engine('mysql://admin:aaggss@localhost/dreadger')

# packet should be or the format given below
# "ABC123100015/9/2014 13:10"
def parsedata(data):
	data = data.strip()
	data = data.split(';')
	device = data[0]
	level = int(data[1])
	time = datetime.strptime( data[2], "%d/%m/%Y %H:%M") #"21/11/06 16:30"
	return (device, level, time)

if __name__ == '__main__':	
	sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	HOST = ''
	PORT = 50002
	try :
		sock.bind((HOST,PORT))

	except socket.error, msg:
		logger.error( 'Bind failed. Error code: ' + str(msg))
		sys.exit()

	logger.info('Socket binding complete')

	session = sessionmaker()
	session.configure(bind=engine)
	while 1:
		data, addr = sock.recvfrom(256)
		try:
			device, level, time = parsedata(data)
			ip,port = addr
			s = session()
			s.add(DieselLevel(device, level, time, ip))
			logger.debug ('Data packet recieved')
			logger.debug('From : %s' %str(addr))
			logger.debug('Device : ' + device)
			logger.debug('Level : %d' %level)
			logger.debug('Time : %s' %(str(time)))

			s.commit()
		except:
			logger.error('Unable to parse the packet')

	s.close() 	
		
