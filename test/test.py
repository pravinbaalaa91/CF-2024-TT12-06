import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, Timer


async def reset_dut(dut, cycles=5):
    """Reset DUT (active low rst_n)."""
    dut.rst_n.value = 0
    await Timer(1, units="ns")
    for _ in range(cycles):
        await RisingEdge(dut.clk)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)


@cocotb.test()
async def pwm_basic_test(dut):
    """Test PWM output for different duty cycles."""
    # Start clock (20 ns period = 50 MHz)
    cocotb.start_soon(Clock(dut.clk, 20, units="ns").start())

    # Apply reset
    await reset_dut(dut)

    # Function to measure duty cycle
    async def measure_duty(dc_val, cycles=256):
        dut.ui_in.value = dc_val
        await RisingEdge(dut.clk)

        ones = 0
        total = 0
        for _ in range(cycles):
            await RisingEdge(dut.clk)
            if dut.uo_out[0].value == 1:
                ones += 1
            total += 1
        return ones / total * 100

    # --- Test cases ---
    for dc_in in [0, 25, 50, 75, 100]:
        measured = await measure_duty(dc_in)
        cocotb.log.info(f"Duty={dc_in}% → Measured ≈ {measured:.1f}%")

        if dc_in == 0:
            assert measured < 5, f"Expected ~0% duty, got {measured:.1f}%"
        elif dc_in == 100:
            assert measured > 95, f"Expected ~100% duty, got {measured:.1f}%"
        else:
            # Allow ±10% tolerance
            assert abs(measured - dc_in) <= 10, f"Duty mismatch: expected {dc_in}%, got {measured:.1f}%"
