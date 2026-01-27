
# Board control

## General information

This folder contains all the code that is responsible for controlling the arduino board and reading the sensors. For compiling and sending the code to the board `arduino-cli` is used. Inside the folder is also included a `makefile` used for setting up the compilation and sending the compiled code to the board.

### Makefile variables and commands

The variables that can be specified are the following

- `BOARD`: Type of arduino board in use (default is`arduino:avr:mega`)
- `PORT`: Port where the board is connected (default `/dev/ttyACM0`)
- `SKETCH`: Location of the main sketch file (default `./main/main.ino`)
- `LIBRARIES`: External libraries used (default empty)

Although more commands are detailed in the makefile itself, here are listed the core commands:

- `all`: Default target, compiles and uploads the code to the board.

- `compile`: Compiles the sketch
- `upload`: Uploads the code to the board
- `clean`: Cleans any unnecessary temporary files
- `install-core`: Installs the necessary drivers for the specified board architecture.

## Board and sensor description

The board used is an Arduino Mega 2560.

For compiling the sketches `arduino-cli` version `1.4.0` was used.

The sensor used are:
- For humidity and temperature a DHT11 Temperature and Humidity module.
- For the light level a KY-018 Photoresistor Module (with a fixed 1kΩ resistor)
- For the soil humidity a HW-103 soil humidity sensor module.
