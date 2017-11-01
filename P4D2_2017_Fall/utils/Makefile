BUILD_DIR = build
PCAP_DIR = pcaps
LOG_DIR = logs

TOPO = topology.json
P4C = p4c-bm2-ss
RUN_SCRIPT = ../../utils/run_exercise.py

source := $(wildcard *.p4)
outfile := $(source:.p4=.json)

compiled_json := $(BUILD_DIR)/$(outfile)

all: run

run: build 
	sudo python $(RUN_SCRIPT) -t $(TOPO) -j $(compiled_json)

stop:
	sudo mn -c

build: dirs $(compiled_json)

$(BUILD_DIR)/%.json: %.p4
	$(P4C) --p4v 16 -o $@ $<

dirs:
	mkdir -p $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)

clean: stop
	rm -f *.pcap
	rm -rf $(BUILD_DIR) $(PCAP_DIR) $(LOG_DIR)
