`default_nettype none

module alu_serial (
    input wire CLK,
    input wire RST,
    input wire Bit_in,
    input wire [2:0] op,
    output reg [6:0] Data_out,
    output reg Done
);

    reg [6:0] A;
    reg [6:0] B;
    reg [3:0] count;
    reg [7:0] suma_ext;

    always @(posedge CLK or negedge RST) begin
        if (!RST) begin
            A        <= 7'b0;
            B        <= 7'b0;
            count    <= 4'd0;
            Data_out <= 7'b0;
            Done     <= 1'b0;
            suma_ext <= 8'b0;
        end
        else begin
            if (count < 4'd7) begin
                A[count] <= Bit_in;
                count    <= count + 4'd1;
            end
            else if (count < 4'd14) begin
                B[count - 4'd7] <= Bit_in;
                count           <= count + 4'd1;
            end
            else if (!Done) begin
                case(op)
                    3'b000: begin
                        suma_ext = {1'b0, A} + {1'b0, B};

                        if (suma_ext > 8'd127)
                            Data_out <= 7'd127;
                        else
                            Data_out <= suma_ext[6:0];
                    end

                    3'b001: Data_out <= A & B;
                    3'b010: Data_out <= A | B;
                    3'b011: Data_out <= A ^ B;

                    3'b100: begin
                        if (A < B)
                            Data_out <= 7'd0;
                        else
                            Data_out <= A - B;
                    end

                    default: Data_out <= 7'd0;
                endcase

                Done <= 1'b1;
            end
        end
    end

endmodule

`default_nettype wire