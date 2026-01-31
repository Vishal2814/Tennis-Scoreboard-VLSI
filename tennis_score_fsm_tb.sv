`timescale 1ns/1ps

module tennis_score_fsm_tb;

    // --------------------------------------------------------
    // Clock & Reset
    // --------------------------------------------------------
    logic clk;
    logic rst_n;

    // --------------------------------------------------------
    // DUT inputs
    // --------------------------------------------------------
    logic p1_point;
    logic p2_point;

    // --------------------------------------------------------
    // DUT outputs
    // --------------------------------------------------------
    logic p1_game_win;
    logic p2_game_win;

    // --------------------------------------------------------
    // DUT instantiation
    // --------------------------------------------------------
    tennis_score_fsm dut (
        .clk(clk),
        .rst_n(rst_n),
        .p1_point(p1_point),
        .p2_point(p2_point),
        .p1_game_win(p1_game_win),
        .p2_game_win(p2_game_win)
    );

    // --------------------------------------------------------
    // Clock generation (10 ns period)
    // --------------------------------------------------------
    initial clk = 0;
    always #5 clk = ~clk;

    // --------------------------------------------------------
    // Test phase indicator (for waveform clarity)
    // --------------------------------------------------------
    typedef enum int {
        PH_RESET      = 0,
        PH_P1_DIRECT  = 1,
        PH_DEUCE_PATH = 2,
        PH_P2_ADV     = 3,
        PH_DONE       = 4
    } phase_t;

    phase_t test_phase;

    // --------------------------------------------------------
    // Human-readable decoded signals
    // --------------------------------------------------------
    int    p1_score_dec;
    int    p2_score_dec;
    string state_name;

    always_comb begin
        case(dut.p1_score)
            0: p1_score_dec = 0;
            1: p1_score_dec = 15;
            2: p1_score_dec = 30;
            3: p1_score_dec = 40;
            default: p1_score_dec = -1;
        endcase

        case(dut.p2_score)
            0: p2_score_dec = 0;
            1: p2_score_dec = 15;
            2: p2_score_dec = 30;
            3: p2_score_dec = 40;
            default: p2_score_dec = -1;
        endcase
    end

    always_comb begin
        case(dut.state)
            dut.S_NORMAL  : state_name = "NORMAL";
            dut.S_DEUCE   : state_name = "DEUCE";
            dut.S_ADV_P1  : state_name = "ADV_P1";
            dut.S_ADV_P2  : state_name = "ADV_P2";
            dut.S_GAME_P1: state_name = "GAME_P1";
            dut.S_GAME_P2: state_name = "GAME_P2";
            default       : state_name = "UNKNOWN";
        endcase
    end

    // --------------------------------------------------------
    // Reset task (active-low)
    // --------------------------------------------------------
    task reset_dut();
        begin
            test_phase = PH_RESET;
            rst_n = 0;
            p1_point = 0;
            p2_point = 0;
            repeat(3) @(posedge clk);
            rst_n = 1;
        end
    endtask

    // --------------------------------------------------------
    // Scoring tasks
    // --------------------------------------------------------
    task p1_scores();
        @(posedge clk); p1_point = 1;
        @(posedge clk); p1_point = 0;
    endtask

    task p2_scores();
        @(posedge clk); p2_point = 1;
        @(posedge clk); p2_point = 0;
    endtask

    // --------------------------------------------------------
    // Initial stimulus
    // --------------------------------------------------------
    initial begin
        reset_dut();

        // ---------- TEST 1: P1 direct win ----------
        test_phase = PH_P1_DIRECT;
        p1_scores(); p1_scores(); p1_scores(); p1_scores();
        repeat(2) @(posedge clk);

        // ---------- TEST 2: Deuce path ----------
        test_phase = PH_DEUCE_PATH;
        p1_scores(); p1_scores(); p1_scores();
        p2_scores(); p2_scores(); p2_scores(); // DEUCE
        p1_scores(); p2_scores(); // ADV_P1 → DEUCE
        p1_scores(); p1_scores(); // ADV_P1 → GAME_P1
        repeat(3) @(posedge clk);

        // ---------- TEST 3: P2 advantage win ----------
        test_phase = PH_P2_ADV;
        p1_scores(); p1_scores(); p1_scores();
        p2_scores(); p2_scores(); p2_scores(); // DEUCE
        p2_scores(); p2_scores(); // ADV_P2 → GAME_P2
        repeat(3) @(posedge clk);

        test_phase = PH_DONE;
        $display("=== SIMULATION COMPLETE ===");
        $finish;
    end

    // --------------------------------------------------------
    // Console scoreboard monitor
    // --------------------------------------------------------
    always @(posedge clk) begin
        if (rst_n && (p1_point || p2_point || p1_game_win || p2_game_win)) begin
            $display("[T=%0t ns][PHASE=%0d][%s][P1=%0d | P2=%0d][WIN1=%0b WIN2=%0b]",
                     $time, test_phase, state_name, p1_score_dec, p2_score_dec, p1_game_win, p2_game_win);
        end
    end

    // --------------------------------------------------------
    // Assertions commented out for ModelSim PE
    // --------------------------------------------------------
    /*
    assert property (@(posedge clk) !(p1_game_win && p2_game_win)) else $fatal("ERROR: Both players won simultaneously!");
    assert property (@(posedge clk) p1_game_win |=> !p1_game_win);
    assert property (@(posedge clk) p2_game_win |=> !p2_game_win);
    assert property (@(posedge clk) !rst_n |-> !(p1_game_win || p2_game_win));
    */

    // --------------------------------------------------------
    // Functional coverage commented out for ModelSim PE
    // --------------------------------------------------------
    /*
    covergroup game_cg @(posedge clk);
        coverpoint dut.state {
            bins normal  = {dut.S_NORMAL};
            bins deuce   = {dut.S_DEUCE};
            bins adv_p1  = {dut.S_ADV_P1};
            bins adv_p2  = {dut.S_ADV_P2};
            bins win_p1  = {dut.S_GAME_P1};
            bins win_p2  = {dut.S_GAME_P2};
        }
        coverpoint dut.p1_score { bins s[] = {[0:3]}; }
        coverpoint dut.p2_score { bins s[] = {[0:3]}; }
        cross dut.state, dut.p1_score, dut.p2_score;
    endgroup

    game_cg cg = new();
    */

endmodule
