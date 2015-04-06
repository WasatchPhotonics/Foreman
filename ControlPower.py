# Based on PowerControl from the Griddle, including writing syslog events for
# tracking the status of the phidget
import unittest, logging, serial, sys, time
#Phidget specific imports
from Phidgets.PhidgetException import PhidgetException
from Phidgets.Devices.InterfaceKit import InterfaceKit

ZERO_RELAY = 0
ONE_RELAY = 1
TWO_RELAY = 2
THREE_RELAY = 3

import logging
import logging.handlers
from WasatchLog import PrintLogHandler

log = logging.getLogger('MyLogger')
log.setLevel(logging.DEBUG)

handler = logging.handlers.SysLogHandler(address = '/dev/log')
log.addHandler(handler)

print_handler = PrintLogHandler()
log.addHandler(print_handler)

#log.debug('this is debug')
#log.critical('this is critical')



class Test(unittest.TestCase):
    def test_01_open_phidget(self):
        powercont = PowerControl()


        self.assertTrue( powercont.open_phidget() )
        self.assertTrue( powercont.close_phidget() )

    def test_02_motor(self):
        powercont = PowerControl()
    

        self.assertTrue( powercont.open_phidget() )
        self.assertTrue( powercont.motor_on() )
        time.sleep(2)
        self.assertTrue( powercont.motor_off() )
        
        self.assertTrue( powercont.close_phidget() )

    def test_03_cycle_zero(self):
        pc = PowerControl()
        self.assertTrue(pc.open_phidget())
        self.assertTrue(pc.zero_on())
        time.sleep(3)
        self.assertTrue(pc.zero_off())

    def test_04_cycle_one(self):
        pc = PowerControl()
        self.assertTrue(pc.open_phidget())
        self.assertTrue(pc.one_on())
        time.sleep(3)
        self.assertTrue(pc.one_off())

    def test_05_toggle_zero(self):
        pc = PowerControl()
        self.assertTrue(pc.toggle_line(ZERO_RELAY))

    def test_05_zero_off(self):
        log.info("Force zero off")
        pc = PowerControl()
        self.assertTrue(pc.open_phidget())
        self.assertTrue(pc.zero_off())
        self.assertTrue(pc.close_phidget() )
    def test_05_zero_on(self):
        log.info("Force zero on")
        pc = PowerControl()
        self.assertTrue(pc.open_phidget())
        self.assertTrue(pc.zero_on())
        self.assertTrue(pc.close_phidget() )

    def test_06_toggle_one(self):
        pc = PowerControl()
        self.assertTrue(pc.toggle_line(ONE_RELAY))

    def test_07_toggle_two(self):
        pc = PowerControl()
        self.assertTrue(pc.toggle_line(TWO_RELAY))

    def test_08_toggle_three(self):
        pc = PowerControl()
        self.assertTrue(pc.toggle_line(THREE_RELAY))

class PowerControl(object):
    ''' PowerControl class wraps language around the 1014_2 -
    PhidgetInterfaceKit 0/0/4 4 relay device. '''
    def __init__(self):
        #log.info("Start of power control object")
        pass

    def open_phidget(self):
        ''' Based on the InterfaceKit-simple.py example from Phidgets, create an
        relay object, attach the handlers, open it and wait for the attachment.
        This function's primarily purpose is to replace the prints with log
        statements.  '''
        try:
            self.interface = InterfaceKit()
        except RuntimeError as e:
            log.critical("Phidget runtime exception: %s" % e.details)
            return 0


        try:
            self.interface.setOnAttachHandler( self.interfaceAttached )
            self.interface.setOnDetachHandler( self.interfaceDetached )
            self.interface.setOnErrorhandler(  self.interfaceError    )
        except PhidgetException as e:
            log.critical("Phidget Exception %i: %s" % (e.code, e.details))
            return 0


        try:
	    #print "Force open relay serial: 290968"
            self.interface.openPhidget()
        except PhidgetException as e:
            log.critical("Phidget Exception %i: %s" % (e.code, e.details))
            return 0


        #log.info("Waiting for attach....")
        try:
            self.interface.waitForAttach(100)
        except PhidgetException as e:
            log.critical("Phidget Exception %i: %s" % (e.code, e.details))
            try:
                self.interface.closePhidget()
            except PhidgetException as e:
                log.critical("Close Exc. %i: %s" % (e.code, e.details))
            return 0
   
        return 1

    #Event Handler Callback Functions
    def interfaceAttached(self, e):
        attached = e.device
        #log.info("interface %i Attached!" % (attached.getSerialNum()))
    
    def interfaceDetached(self, e):
        detached = e.device
        log.info("interface %i Detached!" % (detached.getSerialNum()))
    
    def interfaceError(self, e):
        try:
            source = e.device
            log.critical("Interface %i: Phidget Error %i: %s" % \
                               (source.getSerialNum(), e.eCode, e.description))
        except PhidgetException as e:
            log.critical("Phidget Exception %i: %s" % (e.code, e.details))

    def close_phidget(self):
        try:
            self.interface.closePhidget()
        except PhidgetException as e:
            log.critical("Phidget Exception %i: %s" % (e.code, e.details))
            return 0
        return 1

   
    def change_relay(self, relay=0, status=0):
        ''' Toggle the status of the phidget relay line to low(0) or high(1)'''
        try:
            self.interface.setOutputState(relay, status)
            #self.emit_line_change(relay, status)

        except Exception as e:
            log.critical("Problem setting relay on %s" % e)
            return 0

        return 1

    ''' Convenience functions '''
    def zero_on(self):
        #log.info("Zero relay on")
        return self.change_relay(relay=ZERO_RELAY, status=1)

    def zero_off(self):
        return self.change_relay(relay=ZERO_RELAY, status=0)

    def one_on(self):
        #log.info("one relay on")
        return self.change_relay(relay=ONE_RELAY, status=1)

    def one_off(self):
        return self.change_relay(relay=ONE_RELAY, status=0)


    def two_on(self):
        #log.info("two relay on")
        return self.change_relay(relay=TWO_RELAY, status=1)

    def two_off(self):
        return self.change_relay(relay=TWO_RELAY, status=0)

    def three_on(self):
        #log.info("two relay on")
        return self.change_relay(relay=THREE_RELAY, status=1)

    def three_off(self):
        return self.change_relay(relay=THREE_RELAY, status=0)


    def toggle_line(self, line=0):
        ''' Read the internal state of the specified line, then set the opposite
        state for a toggle function'''
        if not self.open_phidget():
            log.critical("Problem opening phidget")
            return 0

        try:
            curr_state = self.interface.getOutputState(line)
        except Exception as e:
            log.critical("Problem getting relay on %s" % e)
            self.close_phidget()
            return 0

        if not self.change_relay(line, not curr_state):
            log.critical("Problem changing relay")
            return 0

        if not self.close_phidget():
            log.criticla("Problem closing phidget")
            return 0

        return 1



if __name__ == '__main__':
    unittest.main()

