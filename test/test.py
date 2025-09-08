import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer

async def reset_dut(dut):
    dut.rst_n.value = 0
    await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

@cocotb.test()
async def test_pwm_debug(dut):
    cocotb.start_soon(Clock(dut.clk, 10, units="ns").start())
    await reset_dut(dut)
    dut.ui_in.value = 50  # 50% duty cycle
    for cycle in range(20):
        await RisingEdge(dut.clk)
        val0 = dut.uo_out[0].value.integer
        val1 = dut.uo_out[1].value.integer
        cocotb.log.info(f"Cycle={cycle} uo_out[0]={val0}, uo_out[1]={val1}, ui_in={dut.ui_in.value.integer}")
        # Commented assertion for debug
        # assert val0 == val1, "Outputs should match"

