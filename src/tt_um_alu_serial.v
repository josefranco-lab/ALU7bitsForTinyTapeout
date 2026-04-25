`default_nettype none

module tt_um_alu_serial (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // Bidirectional IO input path
    output wire [7:0] uio_out,  // Bidirectional IO output path
    output wire [7:0] uio_oe,   // Bidirectional IO output enable, active high
    input  wire       ena,      // Design enable
    input  wire       clk,      // Clock
    input  wire       rst_n     // Reset active low
);

    wire bit_in;
    wire [2:0] op;
    wire [6:0] data_out;
    wire done;

    // Mapeo de entradas TinyTapeout
    assign bit_in = ui_in[0];
    assign op     = ui_in[3:1];

    alu_serial alu_inst (
        .CLK(clk),
        .RST(rst_n),       // alu_serial usa reset activo en bajo
        .Bit_in(bit_in),
        .op(op),
        .Data_out(data_out),
        .Done(done)
    );

    // Mapeo de salidas TinyTapeout
    assign uo_out[6:0] = data_out;
    assign uo_out[7]   = done;

    // No se usan los pines bidireccionales
    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    // Señales no usadas para evitar warnings
    wire _unused = &{ena, ui_in[7:4], uio_in, 1'b0};

endmodule

`default_nettype wire
