# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

'''import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")

    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, 10, unit="us")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1

    dut._log.info("Test project behavior")

    # Set the input values you want to test
    dut.ui_in.value = 20
    dut.uio_in.value = 30

    # Wait for one clock cycle to see the output values
    await ClockCycles(dut.clk, 1)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    assert dut.uo_out.value == 50

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.'''

# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, RisingEdge


OP_SUM = 0b000
OP_AND = 0b001
OP_OR  = 0b010
OP_XOR = 0b011
OP_SUB = 0b100


def build_ui(bit_in, op):
    """
    ui_in[0]   = Bit_in
    ui_in[3:1] = op[2:0]
    """
    return (op << 1) | (bit_in & 0x1)


async def reset_dut(dut):
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 5)

    dut.rst_n.value = 1
    await ClockCycles(dut.clk, 1)


async def send_bit(dut, bit_value, op):
    dut.ui_in.value = build_ui(bit_value, op)
    await RisingEdge(dut.clk)


async def send_operands(dut, a_value, b_value, op):
    # Enviar A desde LSB hasta MSB
    for i in range(7):
        await send_bit(dut, (a_value >> i) & 1, op)

    # Enviar B desde LSB hasta MSB
    for i in range(7):
        await send_bit(dut, (b_value >> i) & 1, op)

    # Pulso extra para que la ALU calcule
    await send_bit(dut, 0, op)


async def run_test(dut, a, b, op, expected):
    await reset_dut(dut)

    await send_operands(dut, a, b, op)

    data_out = int(dut.uo_out.value) & 0x7F
    done = (int(dut.uo_out.value) >> 7) & 0x1

    dut._log.info(
        f"A={a} B={b} op={op:03b} Data_out={data_out} Done={done} Expected={expected}"
    )

    assert done == 1, "Done no se activó"
    assert data_out == expected, (
        f"Resultado incorrecto: A={a}, B={b}, op={op:03b}, "
        f"esperado={expected}, obtenido={data_out}"
    )


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start ALU serial 7 bits test")

    # Reloj de prueba. No tiene que ser 50 MHz para simulación funcional.
    clock = Clock(dut.clk, 20, unit="ns")
    cocotb.start_soon(clock.start())

    # Suma normal: 5 + 3 = 8
    await run_test(dut, 5, 3, OP_SUM, 8)

    # Suma con saturación: 100 + 60 = 160 -> 127
    await run_test(dut, 100, 60, OP_SUM, 127)

    # Suma límite: 127 + 1 -> 127
    await run_test(dut, 127, 1, OP_SUM, 127)

    # Resta normal: 10 - 6 = 4
    await run_test(dut, 10, 6, OP_SUB, 4)

    # Resta negativa saturada: 3 - 5 -> 0
    await run_test(dut, 3, 5, OP_SUB, 0)

    # AND: 5 & 3 = 1
    await run_test(dut, 5, 3, OP_AND, 1)

    # OR: 5 | 3 = 7
    await run_test(dut, 5, 3, OP_OR, 7)

    # XOR: 5 ^ 3 = 6
    await run_test(dut, 5, 3, OP_XOR, 6)

    dut._log.info("All ALU serial tests passed")
