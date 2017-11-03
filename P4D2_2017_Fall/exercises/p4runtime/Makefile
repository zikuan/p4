include ../../utils/Makefile

# Override build method to use simple_switch_grpc target
run: build
	sudo python $(RUN_SCRIPT) -t $(TOPO) -b simple_switch_grpc

# Override p4c step to also produce p4info file
P4INFO_ARGS = --p4runtime-file $(basename $@).p4info --p4runtime-format text
$(BUILD_DIR)/%.json: %.p4
	$(P4C) --p4v 16 $(P4INFO_ARGS) -o $@ $<
