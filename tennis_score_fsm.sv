module tennis_score_fsm (
    input  logic clk,
    input  logic rst_n,

    input  logic p1_point,     // 1-cycle pulse when Player 1 wins a point
    input  logic p2_point,     // 1-cycle pulse when Player 2 wins a point

    output logic p1_game_win,  // asserted for 1 cycle
    output logic p2_game_win   // asserted for 1 cycle
);

    // --------------------------------------------------------
    // State encoding
    // --------------------------------------------------------
    typedef enum logic [2:0] {
        S_NORMAL   = 3'd0,
        S_DEUCE    = 3'd1,
        S_ADV_P1   = 3'd2,
        S_ADV_P2   = 3'd3,
        S_GAME_P1 = 3'd4,
        S_GAME_P2 = 3'd5
    } state_t;

    state_t state, next_state;

    // --------------------------------------------------------
    // Score registers
    // 0 = 0
    // 1 = 15
    // 2 = 30
    // 3 = 40
    // --------------------------------------------------------
    logic [1:0] p1_score;
    logic [1:0] p2_score;

    // --------------------------------------------------------
    // Sequential logic (state + datapath)
    // --------------------------------------------------------
    always_ff @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state    <= S_NORMAL;
            p1_score <= 2'd0;
            p2_score <= 2'd0;
        end
        else begin
            state <= next_state;

            // Score update only in NORMAL state
            if (state == S_NORMAL) begin
                if (p1_point && p1_score < 2'd3)
                    p1_score <= p1_score + 2'd1;
                if (p2_point && p2_score < 2'd3)
                    p2_score <= p2_score + 2'd1;
            end

            // Reset scores after game win
            if (state == S_GAME_P1 || state == S_GAME_P2) begin
                p1_score <= 2'd0;
                p2_score <= 2'd0;
            end
        end
    end

    // --------------------------------------------------------
    // Combinational next-state logic
    // --------------------------------------------------------
    always_comb begin
        // Defaults
        next_state  = state;
        p1_game_win = 1'b0;
        p2_game_win = 1'b0;

        case (state)

            // ---------------- NORMAL ----------------
            S_NORMAL: begin
                // Deuce condition
                if (p1_score == 2'd3 && p2_score == 2'd3)
                    next_state = S_DEUCE;

                // Direct game win
                else if (p1_score == 2'd3 && p2_score < 2'd3 && p1_point)
                    next_state = S_GAME_P1;

                else if (p2_score == 2'd3 && p1_score < 2'd3 && p2_point)
                    next_state = S_GAME_P2;
            end

            // ---------------- DEUCE ----------------
            S_DEUCE: begin
                if (p1_point)
                    next_state = S_ADV_P1;
                else if (p2_point)
                    next_state = S_ADV_P2;
            end

            // ---------------- ADVANTAGE P1 ----------------
            S_ADV_P1: begin
                if (p1_point)
                    next_state = S_GAME_P1;
                else if (p2_point)
                    next_state = S_DEUCE;
            end

            // ---------------- ADVANTAGE P2 ----------------
            S_ADV_P2: begin
                if (p2_point)
                    next_state = S_GAME_P2;
                else if (p1_point)
                    next_state = S_DEUCE;
            end

            // ---------------- GAME WIN STATES ----------------
            S_GAME_P1: begin
                p1_game_win = 1'b1;
                next_state  = S_NORMAL;
            end

            S_GAME_P2: begin
                p2_game_win = 1'b1;
                next_state  = S_NORMAL;
            end

            default: begin
                next_state = S_NORMAL;
            end

        endcase
    end

endmodule
