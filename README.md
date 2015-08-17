Adapteva Parallella Screener (The Foreman) instructions:

Wasatch Photonics uses Adapteva Parallella SKU P1601-DK03's as an embedded linux
system. Core capabilities required include a USB bus that is available at least
83% of the time on boot up. A screener was created to allow us to find the
incoming Parallella boards that meet this level of usb availability. This setup
consists of 4 Parallella DC adapters connected to a Phidgets software controlled
relay. This relay turns on the devices for 35 seconds, issues a 'lsusb' command
on each device, and stores the status of the usb availability. The device is
then turned off for 75 seconds, then the process is repeated. This will produce
summary results like:

04:4F:8B:00:2C:6E Pass: 1553, Fail: 1058  (55.56% failure rate)
04:4F:8B:00:2C:7C Pass: 610,  Fail: 1999  (86.42% failure rate)
04:4F:8B:00:2C:72 Pass: 2596, Fail: 14    ( 1.23% failure rate)
(These are from: http://wasatchcookbook.com/static/orig_results.html)

You can see live results here:
http://wasatchcookbook.com/static/foreman_results.html

Read all about Parallella USB issues here:
https://parallella.org/forums/viewtopic.php?f=50&t=1650&start=40#p13290

Here is what the Foreman looks like in practice:
![foreman hardware](https://parallella.org/forums/download/file.php?id=412 "foreman hardware")


copy the disk image onto an sd card (see parallela instructions)
These instructions use: ubuntu-14.04-headless-z7010-20150130.1.img

Boot the system, find it on the network with:
nmap -p22 --open 192.168.1.0/24

Find the entry like:
Nmap scan report for 192.168.1.xx
Host is up (0.00034s latency).
PORT   STATE SERVICE
22/tcp open  ssh
MAC Address: 04:4F:8B:00:2C:7C (Adapteva)

cat test_key_rsa.pub | ssh parallella@192.168.1.xx "mkdir ~/.ssh/; cat >> ~/.ssh/authorized_keys"
(enter password: parallella)

SSH to the device, change the ip address to boot static by replacing the
contents of /etc/network/interfaces.d/eth0 with:

auto eth0
iface eth0 inet static
address 192.168.1.15x
gateway 192.168.1.1
netmask 255.255.255.0
dns-nameservers 8.8.8.8 8.8.4.4


Reboot the device and verify it comes up on the network with the static boot
address.

Repeat the process above for every SD card to be used in the test script. For
example, the test here at Wasatch Photonics Systems Division is setup to screen
4 Parallelas simultaneous with IP's 150-153.

On the control system, install the phidgets usb drivers. Run the control program
with the command:

python -u ForemanTest.py

This will begin the power cycling procedure and create a file with the format:

192.168.1.153 2015-04-01 ... Device 001: ... HWaddr 04:4f:8b:00:2c:72 
192.168.1.150 2015-04-01 ... libusb: -99 ... HWaddr 04:4f:8b:00:2c:7c

Where any entry with libusb: -99 signifies a usb failure, and the HWaddr is the
mac address for the parallela.

Separate programs can be used to process this information into more readable
data as shown on the page:
http://wasatchcookbook.com/static/foreman_results.html
Raw data is here:
http://wasatchcookbook.com/static/ip_and_mac.log
