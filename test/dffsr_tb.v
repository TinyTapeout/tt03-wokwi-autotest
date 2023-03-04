// SPDX-FileCopyrightText: © 2022 Uri Shaked <uri@wokwi.com>
// SPDX-License-Identifier: Apache2.0

`timescale 1ns / 1ps
// 
`default_nettype none

module test_dffsr ();
  reg clk;
  reg data;
  reg set;
  reg reset;
  wire [7:0] io_out;
  wire q = io_out[7];
  wire notq = io_out[0];

  user_module_358289719320459265 dut (
  `ifdef GL_TEST
      .vccd1( 1'b1),
      .vssd1( 1'b0),
  `endif
      .io_in ({6'bxxxx, set, data, reset, clk}),
      .io_out(io_out)
  );

  initial begin
    clk = 0;
    forever begin
      #5 clk = ~clk;
    end
  end

  initial begin
    $dumpfile("dffsr_tb.vcd");
    $dumpvars(0, test_dffsr);
  end
endmodule
