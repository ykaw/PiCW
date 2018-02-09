# PiCW
A morse code keyer running on Raspberry Pi

## GPIO ports
* Two input ports for iambic paddles
  * supporting mode A and mode B
  * bug key emulation
  * side swiper emulation

* An input port for straight key

* An output port for TX control

* The PWM output for side tone

## CLI interface on RPi
* send message
  * with keyboard
  * from text files
* record/replay keying  
(both computer and manual keying)
* training mode  
with arbitrary set of characters
* variable gap length between every letters  
(especially useful for training)
* enable/disable
  * iambic paddles
  * straight key
  * tx control line
  * side tone (also can change freq.)
  
# See also
* docs/schematic.txt - schematic diagram of GPIO ports
* Supporting GPIO libraries
  * [pigpio](http://abyz.me.uk/rpi/pigpio/)(recommended)
  * [RPi.GPIO](https://sourceforge.net/projects/raspberry-gpio-python/)
