import re
import csv

# ------------------------------
# Input / Output
# ------------------------------
input_file = r"D:\VLSI\Tennis Score Board\simulation\modelsim\msim_transcript"
output_file = r"D:\VLSI\Tennis Score Board\CSV_of_Scores.csv"

# ------------------------------
# Regex pattern to extract fields
# ------------------------------
pattern = re.compile(
    r"#?\s*\[T=(\d+)\s*ns\]\[PHASE=(\d+)\]\[(\w+)\]\[P1=(\d+)\s*\|\s*P2=(\d+)\]\[WIN1=(\d)\s*WIN2=(\d)\]"
)

# ------------------------------
# CSV Header
# ------------------------------
header = ["Time_ns", "Phase", "State", "P1_Score", "P2_Score", "WIN1", "WIN2"]

# ------------------------------
# Parse log and write CSV
# ------------------------------
with open(input_file, "r") as f_in, open(output_file, "w", newline="") as f_out:
    writer = csv.writer(f_out)
    writer.writerow(header)

    for line in f_in:
        line = line.strip()
        # Remove leading '#' and spaces
        line = line.lstrip("# ").strip()
        if line.startswith("[T="):  # Only process scoreboard lines
            match = pattern.match(line)
            if match:
                time_ns, phase, state, p1, p2, win1, win2 = match.groups()
                writer.writerow([time_ns, phase, state, p1, p2, win1, win2])

print(f"CSV successfully generated: {output_file}")
