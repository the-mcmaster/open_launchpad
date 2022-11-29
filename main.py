import io
import time
import sys
import logging as log

from Driver import Driver

DEV = Driver()
log.basicConfig(level=log.INFO, format='%(asctime)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')

if __name__ == "__main__":
    success = False
    while True:
        try:
            button = DEV.input()
            DEV.update(button)
            success = True
        except:
            log.info("Trying to reconnect to device")
            try:
                DEV = Driver()
            except:
                log.error("Fatal error")
                sys.exit(1)
        
        if success:
            DEV.draw()