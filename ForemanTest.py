# Turn on the relay to the parallelas, let it run, check the usb bus status,
# record and process. Power cycle.
import unittest, logging, serial, sys, time, datetime, pygal
from ControlPower import PowerControl

logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
    level=logging.DEBUG, filename=None)
log = logging.getLogger()

class Test(unittest.TestCase):
    def runProcess(self, exe):    
        import subprocess
        p = subprocess.Popen(exe, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        while(True):
            retcode = p.poll() #returns None while subprocess is running
            line = p.stdout.readline()
            yield line
            if(retcode is not None):
                break


    def relay_on(self, name="zero"):
        ''' Create a power control object, toggle the status in question.'''
        pc = PowerControl()
            
        self.assertTrue(pc.open_phidget())
        if name == "zero":
            self.assertTrue(pc.zero_on())
        elif name == "one":
            self.assertTrue(pc.one_on())
        elif name == "two":
            self.assertTrue(pc.two_on())
        elif name == "three":
            self.assertTrue(pc.three_on())
        else:
            print "Unknown relay"
            sys.exit(1)

        self.assertTrue(pc.close_phidget())

    def relay_off(self, name="zero"):
        ''' Create a power control object, toggle the status in question.'''
        pc = PowerControl()
            
        self.assertTrue(pc.open_phidget())
        if name == "zero":
            self.assertTrue(pc.zero_off())
        elif name == "one":
            self.assertTrue(pc.one_off())
        elif name == "two":
            self.assertTrue(pc.two_off())
        elif name == "three":
            self.assertTrue(pc.three_off())
        else:
            print "Unknown relay"
            sys.exit(1)

        self.assertTrue(pc.close_phidget())

    def ssh_lsusb_mac(self, suffix):
        ''' Run the specified shell file with the suffix. '''
        # lsusb_mac.sh is a script with contents:
        # ssh -i ./test_key_rsa parallella@192.168.1.$1 \
        #   "lsusb; ifconfig | grep eth"
        text = ""
        script_file = "./lsusb_mac.sh"
        for line in self.runProcess(['bash', script_file, suffix]):
            text += line
        return text

    def test_30_continuous(self):
        ''' Turn on all 4 relays, look for results at the defined ip addresses,
        store lsusb status and mac addresses.'''
    
        logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s',
                level=logging.DEBUG)
        log = logging.getLogger()
   
  
        power_on_wait = 35  # as short as possible
        power_off_wait = 75 # off at least twice as long as on
        stop_test = False
        total_tests = 0
 
        ip_list = ['150', '151', '152', '153']
        name_list = ['zero', 'one', 'two', 'three']

        while not stop_test: 
            for item in name_list:
                self.relay_on(item)

            log.info("Power on, wait %s seconds" % power_on_wait)
            time.sleep(power_on_wait)

            cmd_result = "intialize"
            for ip_item in ip_list:
                try:
                    cmd_result = self.ssh_lsusb_mac(ip_item)
                except Exception as exc:
                    log.critical("Failure to get lsusb results %s" % str(exc))
                    self.assertEquals("Failure to get", "lsusb results")

                cmd_result = cmd_result.replace('\n', ' ')

                timestamp = datetime.datetime.now()
                out_file = open("ip_and_mac.log", 'a')
                out_file.write("192.168.1.%s %s %s" % (ip_item, timestamp, cmd_result))
                out_file.write('\n')
                log.info("192.168.1.%s %s %s" % (ip_item, timestamp, cmd_result))
                out_file.close()

            for item in name_list:
                self.relay_off(item)

            log.info("Power off, wait %s seconds" % power_off_wait)
            time.sleep(power_off_wait)

            total_tests += 1
            log.info("Completed test: %s" % total_tests)

if __name__ == '__main__':
    unittest.main()
