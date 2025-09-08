import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

async def reset_dut(dut):
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_reset_and_initial_state(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    cocotb.log.info(f"[reset] uo_out[0]={dut.uo_out[0].value.integer}, uo_out[1]={dut.uo_out[1].value.integer}")
    assert dut.uo_out[0].value.integer == 0, "pwm_out should be low after reset"
    assert dut.uo_out[1].value.integer == 0, "pwm_out1 should be low after reset"

@cocotb.test()
async def test_pwm_zero_duty_cycle(dut):
    await reset_dut(dut)
    dut.ui_in.value = 0  # 0% duty cycle
    for cycle in range(260):
        await RisingEdge(dut.clk)
        cocotb.log.info(f"[zero duty] cycle={cycle} uo_out[0]={dut.uo_out[0].value.integer} uo_out[1]={dut.uo_out[1].value.integer}")
        assert dut.uo_out[0].value.integer == 0, "pwm_out should stay low for 0% duty"
        assert dut.uo_out[1].value.integer == 0, "pwm_out1 should stay low for 0% duty"

@cocotb.test()
async def test_pwm_full_duty_cycle(dut):
    await reset_dut(dut)
    dut.ui_in.value = 100  # 100% duty cycle
    for cycle in range(260):
        await RisingEdge(dut.clk)
        cocotb.log.info(f"[full duty] cycle={cycle} uo_out[0]={dut.uo_out[0].value.integer} uo_out[1]={dut.uo_out[1].value.integer}")
        assert dut.uo_out[0].value.integer == 1, "pwm_out should stay high for 100% duty"
        assert dut.uo_out[1].value.integer == 1, "pwm_out1 should stay high for 100% duty"

@cocotb.test()
async def test_pwm_mid_duty_cycle(dut):
    await reset_dut(dut)
    dut.ui_in.value = 50  # 50% duty cycle
    high_count = 0
    total_cycles = 256
    for cycle in range(total_cycles):
        await RisingEdge(dut.clk)
        val = dut.uo_out[0].value.integer
        cocotb.log.info(f"[mid duty] cycle={cycle} uo_out[0]={val}")
        high_count += val
    cocotb.log.info(f"[mid duty] high_count={high_count} after {total_cycles} cycles")
    assert abs(high_count - (total_cycles // 2)) <= 2, "pwm_out should be ~50% high at 50% duty"

@cocotb.test()
async def test_pwm_out_and_pwm_out1_equal(dut):
    await reset_dut(dut)
    for duty in [0, 10, 50, 100]:
        dut.ui_in.value = duty
        cocotb.log.info(f"[equal test] duty={duty}")
        await Timer(5000, units="ns")
        for cycle in range(10):
            await RisingEdge(dut.clk)
            val0 = dut.uo_out[0].value.integer
            val1 = dut.uo_out[1].value.integer
            cocotb.log.info(f"[equal test] cycle={cycle} uo_out[0]={val0} uo_out[1]={val1}")
            assert val0 == val1, "pwm_out and pwm_out1 must be equal"

@cocotb.test()
async def test_pwm_edge_cases(dut):
    await reset_dut(dut)
    # Lower boundary just above zero
    dut.ui_in.value = 1
    cocotb.log.info("[edge] duty=1")
    await Timer(3000, units="ns")
    # Upper boundary just below 100
    dut.ui_in.value = 99
    cocotb.log.info("[edge] duty=99")
    await Timer(3000, units="ns")
