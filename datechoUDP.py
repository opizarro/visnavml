# plays back a DAT log file via UDP
# used to approximately test UDP traffic expected in real-time

import socket
import sys
from time import sleep
if len(sys.argv) < 2:
    print 'Usage: ' +sys.argv[0] + ' filename port\n'
    sys.exit(-1)

# e.g. python datechoUDP.py /Users/opizarro/data/sentry201307/oscar-sample-data/sentry125/raw/dvlnav/bigfile.DAT 12350

UDP_IP = "127.0.0.1"
UDP_PORT = int(sys.argv[2])


print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT


sock = socket.socket(socket.AF_INET, # Internet
                     socket.SOCK_DGRAM) # UDP
ins = open( sys.argv[1], "r" )
i=0
for line in ins:
    parsed=line.split(' ',3)
    if len(parsed) >3:
        sock.sendto(parsed[3], (UDP_IP, UDP_PORT))
    else:
        if parsed[0] != '\r\n':
            print 'Message ', i, ' failed to parse ',parsed

    sleep(0.005)
    i=i+1
    if i % 20 == 0:
        sys.stdout.write('.')
        sys.stdout.flush()
sys.stdout.write('\nDone\n')
