import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, FallingEdge, Timer

async def reset_dut(dut):
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_reset_and_initial_state(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    assert dut.uo_out.value == 0, "Output should be low after reset"
    assert dut.uo_out[1].value == 0, "pwm_out1 should also be low after reset"

@cocotb.test()
async def test_pwm_zero_duty_cycle(dut):
    await reset_dut(dut)
    dut.ui_in.value = 0  # 0% duty cycle
    for _ in range(260):
        await RisingEdge(dut.clk)
        assert dut.uo_out[0].value == 0, "Output should stay low for 0% duty"

@cocotb.test()
async def test_pwm_full_duty_cycle(dut):
    await reset_dut(dut)
    dut.ui_in.value = 100  # 100% duty cycle (assuming value 100 represents 100%)
    for _ in range(260):
        await RisingEdge(dut.clk)
        assert dut.uo_out[0].value == 1, "Output should stay high for 100% duty"

@cocotb.test()
async def test_pwm_mid_duty_cycle(dut):
    await reset_dut(dut)
    # Test 50% duty cycle
    dut.ui_in.value = 50
    high_count = 0
    total_cycles = 256
    for _ in range(total_cycles):
        await RisingEdge(dut.clk)
        high_count += int(dut.uo_out[0].value)
    assert abs(high_count - (total_cycles // 2)) <= 2, "Output should be ~50% high at 50% duty"

@cocotb.test()
async def test_pwm_out_and_pwm_out1_equal(dut):
    await reset_dut(dut)
    for duty in [0, 10, 50, 100]:
        dut.ui_in.value = duty
        await Timer(5000, units="ns")
        for _ in range(10):
            await RisingEdge(dut.clk)
            assert dut.uo_out[0].value == dut.uo_out[1].value, "pwm_out and pwm_out1 must be equal"

@cocotb.test()
async def test_pwm_edge_cases(dut):
    await reset_dut(dut)
    # Test lower boundary just above zero
    dut.ui_in.value = 1
    await Timer(3000, units="ns")
    # Test upper boundary just below 100
    dut.ui_in.value = 99
    await Timer(3000, units="ns")
