ARDUINO_CLI   := arduino-cli
BOARD         := arduino:avr:mega
SKETCH        := ./main/main.ino

.PHONY: all compile clean

all: compile

compile:
	$(ARDUINO_CLI) compile \
	  --fqbn $(BOARD) \
	  $(SKETCH)

upload: compile
	$(ARDUINO_CLI) upload -p $(PORT) --fqbn $(BOARD) $(SKETCH)

clean:
	rm -rf .arduino*

list-boards:
	$(ARDUINO_CLI) board listall

update-index:
	$(ARDUINO_CLI) core update-index

install-core:
	$(ARDUINO_CLI) core install arduino:avr
	$(ARDUINO_CLI) lib install "DHT sensor library"
	$(ARDUINO_CLI) lib install "Adafruit Unified Sensor"
