# ChocoRobo - Autonomous Chocolate Delivery Robot

By bbtinkerer (<http://bb-tinkerer.blogspot.com/>)

## Description

Simple and easy to build face following robot with off the shelf parts for anyone to build. For use on Adafruit's Circuit Playground Express (CPX) and Crickit. ChocoRobo is connected to a Google AIY Vision that sends data serially. Google AIY Vision sends the mid X coordinate of the detected face along with the size of the bounding box around the face. This code then adjust the left and right motor speeds to movet he robot towards the direction of the face. Also, the NeoPixels on the CPX light up in the direction of the face.

Project documention on [hackster.io](https://www.hackster.io/bbtinkerer/chocorobo-autonomous-chocolate-delivery-robot-597fd0).

YouTube Videos

* [ChocoRobo - Autonomous Chocolate Delivery Robot](https://youtu.be/YWtPi1448u0)
* [ChocoRobo - Autonomous Chocolate Delivery Robot Info](https://youtu.be/wd7FyPMLFyc)
* [ChocoRobo - Autonomous Chocolate Delivery Robot Build](https://youtu.be/Vt1zGyjBj6I)

## Requirements

* [Circuit Playground Express](https://learn.adafruit.com/adafruit-circuit-playground-express?view=all) - Follow instructions on setup, the code requires CircuitPython v3.
* [Adafruit CRICKIT for Circuit Playground Express](https://learn.adafruit.com/adafruit-crickit-creative-robotic-interactive-construction-kit?view=all)
* [Google AIY  Vision Kit](https://aiyprojects.withgoogle.com/vision/) - Used image aiyprojects-2018-08-03.img, the image on the included SD card was too old and didn't include the video streaming server.

## Installation

### Circuit Playground Express

Follow the instructions at Adafruit to copy the code.py from the CPX directory to the Circuit Playground Express.

### Google AIY Vision Kit

Need to enable UART on the Raspberry Pi (reference: [The Raspberry Pi UARTs](https://www.raspberrypi.org/documentation/configuration/uart.md)).

First disable Linux's use of console UART. Enter the following at the console:

```
$ sudo raspi-config
```

1. Choose option 5.
2. Choose P6 Serial.
3. Would you like a login shell to be accessible over serial? Choose No.
4. Would you like the serial port hardware to be enabled? Choose Yes.
5. Confirm The serial login shell is disabled. The serial interface is enabled. Choose Ok.
6. Choose Finish.
7. Would you like to reboot now? Choose No.

Make a copy of /boot/config.txt. Enter the following at the console (I like vim, use whatever text editor you like):

```
$ cd /boot
$ sudo cp config.txt config.bak.txt
$ sudo vim config.txt
```

Append the following to the bottom of config.txt:

```
# Disable the Bluetooth device and restores UART0/ttyAMA0 to GPIOs 14 and 15.
dtoverlay=pi3-disable-bt
```

Disable the system service that initialises the modem so it doesn't use the UART.

```
$ sudo systemctl disable hciuart
```

Should see response of:

```
Removed /etc/systemd/system/multi-user.target.wants/hciuart.service.
```

Replace the joy_detection_demo.py located in the ~/AIY-projects-python/src/examples/vision/joy/ directory of the Vision Kit with the joy_detection_demo.py from the RaspberryPi directory from this repo.

Reboot.

```
$ sudo shutdown -r now
```

## Configuration

There are some settings towards the top of code.py that will need adjustments depending on your hardware and your desired behavior of the robot. The following settings will most likely need tweaking:

* **MAX_DATA_IN_TIME_MARGIN** - Time in seconds to allow FaceBot to keep moving after the last time received data. Lower if overturning, but too low makes for a twitchy robot.
* **MOTOR_BASE_SPEED_RIGHT/MOTOR_BASE_SPEED_LEFT** - Base speeds for the motors. Not all motors are the same so may need to tweak where they rotate at the same starting speed.
* **MOTOR_RIGHT_ERROR_CORRECTION/MOTOR_LEFT_ERROR_CORRECTION** - I had to put in some correction for the motor speeds, I just guessed and trial and error till looked right. The left motor was slower than the right so needed more speed and vice versa for the right motor.
* **Kp/Kd** - Constants to do proportional and derivative control of movement, you may need to tweak to get your bot to move smoothly.
* **MAX_FACE_WIDTH** - Stops the robot from moving when the face exceeds this width so the bot doesn't run into the person.

## Known Issues

If you discover any bugs, feel free to create an issue on GitHub fork and
send a pull request.


## Authors

* bbtinkerer (https://github.com/bbtinkerer/)


## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create new Pull Request


## License

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see <http://www.gnu.org/licenses/>.