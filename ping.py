import subprocess
import os
import re
node = "planetlab1.inf.ethz.ch"
output = os.popen('ping ' + node + " -c 5 | egrep \"packet loss|rtt\"").read()
print output

match = re.search('([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)/([\d]*\.[\d]*)', output)

if match:
    ping_min = match.group(1)
    ping_avg = match.group(2)
    ping_max = match.group(3)

match = re.search('(\d*)% packet loss', output)
if match:
    pkt_loss = match.group(1)

print ping_min
print ping_avg
print ping_max
