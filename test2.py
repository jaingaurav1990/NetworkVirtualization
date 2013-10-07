import logging

logging.basicConfig(filename="logfile.txt", level = logging.DEBUG, format = '%(asctime)s %(levelname)s %(message)s')
logging.info("First log line")
