
module pwm (
    input clk,
    input reset,
    input wire [6:0] dc,
    output reg pwm_out,
    output reg pwm_out1
);
    reg [7:0] count;
    wire [7:0] threshold;

    assign threshold = (dc * 255) / 100;

    always @(posedge clk or negedge reset) begin
        if (!reset) begin
            count <= 8'd0;
            pwm_out <= 0;
            pwm_out1 <= 0;
        end else begin
            count <= count + 1;

            if (threshold == 0) begin
                pwm_out <= 0;
            end else if (dc >= 7'd100) begin
                pwm_out <= 1;
            end else if (count <= threshold) begin
                pwm_out <= 1;
            end else begin
                pwm_out <= 0;
            end

            pwm_out1 <= pwm_out;
        end
    end
endmodule
