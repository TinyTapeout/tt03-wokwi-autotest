# SPDX-FileCopyrightText: © 2022 Uri Shaked <uri@wokwi.com>
# SPDX-License-Identifier: Apache2.0

import os
import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer


async def make_clock(dut, clock_mhz):
    clk_period_ns = round(1 / clock_mhz * 1000, 2)
    dut._log.info("input clock = %d MHz, period = %.2f ns" %
                  (clock_mhz, clk_period_ns))
    clock = Clock(dut.clk, clk_period_ns, units="ns")
    clock_sig = cocotb.fork(clock.start())
    return clock_sig


@cocotb.test()
async def test_dffsr(dut):
    i_data = dut.data
    i_set = dut.set
    i_reset = dut.reset
    o_q = dut.q
    o_notq = dut.notq

    # Initialize the flip-flop, reset it, and wait for the clock
    i_reset.value = 1
    i_set.value = 0
    i_data.value = 0
    await ClockCycles(dut.clk, 2)

    assert o_q.value == 0
    assert o_notq.value == 1

    # Toggle the data a few times, and observe that the output is not changing (because the reset is active)
    i_data.value = 1
    await ClockCycles(dut.clk, 2)
    assert o_q.value == 0
    assert o_notq.value == 1

    i_data.value = 0
    await ClockCycles(dut.clk, 2)
    assert o_q.value == 0
    assert o_notq.value == 1

    i_data.value = 1
    await ClockCycles(dut.clk, 2)
    assert o_q.value == 0
    assert o_notq.value == 1

    # Release the reset, and observe that the output is now changing on the clock's rising edge
    i_reset.value = 0
    await ClockCycles(dut.clk, 2)
    assert o_q.value == 1
    assert o_notq.value == 0

    i_data.value = 0
    await ClockCycles(dut.clk, 2)
    assert o_q.value == 0
    assert o_notq.value == 1

    # Set the flip-flop, and observe that the output changes (almost) immediately
    await Timer(1, units='ns')
    i_set.value = 1
    await Timer(1, units='ps')
    assert o_q.value == 1
    assert o_notq.value == 0

    # Release the set, and observe that the output goes back to low
    await Timer(1, units='ns')
    i_set.value = 0
    await Timer(10, units='ps')
    assert o_q.value == 1
    assert o_notq.value == 0

    await ClockCycles(dut.clk, 2)
    assert o_q.value == 0
    assert o_notq.value == 1

    i_data.value = 1
    await ClockCycles(dut.clk, 2)
    assert o_q.value == 1
    assert o_notq.value == 0

    # Reset the flip-flop, and observe that the output changes (almost) immediately
    await Timer(1, units='ns')
    i_reset.value = 1
    await Timer(10, units='ps')
    assert o_q.value == 0
    assert o_notq.value == 1

    # Release the reset, and observe that the output goes back to high
    await Timer(1, units='ns')
    i_reset.value = 0
    await Timer(10, units='ps')
    assert o_q.value == 0
    assert o_notq.value == 1

    await ClockCycles(dut.clk, 2)
    assert o_q.value == 1
    assert o_notq.value == 0

    # Test that both set and reset can be active at the same time (reset takes priority)
    await Timer(1, units='ns')
    i_set.value = 1
    i_reset.value = 1
    await Timer(10, units='ps')
    assert o_q.value == 0
    assert o_notq.value == 1

    # Release both, data should go back to high on next clock
    await Timer(1, units='ns')
    i_set.value = 0
    await Timer(1, units='ps')
    i_reset.value = 0
    await Timer(10, units='ps')
    assert o_q.value == 0
    assert o_notq.value == 1

    await ClockCycles(dut.clk, 2)
    assert o_q.value == 1
    assert o_notq.value == 0

    # Finally, test a sequence of set/reset without clock changes
    await Timer(1, units='ns')
    i_reset.value = 1
    await Timer(10, units='ps')
    assert o_q.value == 0
    assert o_notq.value == 1

    await Timer(1, units='ns')
    i_reset.value = 0
    i_set.value = 1
    await Timer(10, units='ps')
    assert o_q.value == 1
    assert o_notq.value == 0

    await Timer(1, units='ns')
    i_reset.value = 0
    i_set.value = 0
    await Timer(10, units='ps')
    assert o_q.value == 1
    assert o_notq.value == 0

    await Timer(1, units='ns')
    i_reset.value = 1
    i_set.value = 0
    await Timer(10, units='ps')
    assert o_q.value == 0
    assert o_notq.value == 1

    # and a few more clock cycles for padding
    await ClockCycles(dut.clk, 2)
