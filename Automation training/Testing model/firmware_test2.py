import serial
import time
import re
import os
from datetime import datetime
import webbrowser

# Configuration
PORT = 'COM4'  # Change to your correct port
BAUDRATE = 57600
EXPECTED_FIRMWARE = "1.0.0"
DELAY_EXPECTED = 5
TIME_TOLERANCE = 0.3
TEST_DURATION = 30

# Output folder
output_folder = "firmware_test_report_pages"
os.makedirs(output_folder, exist_ok=True)

# Status flags
firmware_found = False
firmware_correct = False
firmware_first = False
led_pattern_valid = True
led_timing_valid = True
led_sequence = []
log_lines = []

# Serial reading
try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=1)
    time.sleep(2)
    start_time = time.time()
    line_count = 0
    previous_led = None
    first_led_interval_skipped = False

    while time.time() - start_time < TEST_DURATION:
        if ser.in_waiting > 0:
            raw_line = ser.readline().decode(errors='ignore').strip()
            if not raw_line:
                continue

            timestamp = datetime.now().strftime("[%H:%M:%S]")
            line_count += 1
            log_lines.append(f"{timestamp} {raw_line}")

            # Firmware check
            if not firmware_found:
                match = re.match(r"Firmware Version:\s*v?(\d+\.\d+\.\d+)", raw_line)
                if match:
                    actual_version = match.group(1)
                    firmware_found = True
                    firmware_correct = actual_version == EXPECTED_FIRMWARE
                    firmware_first = (line_count == 1)

            # LED check
            if "LED ON" in raw_line or "LED OFF" in raw_line:
                state = "ON" if "LED ON" in raw_line else "OFF"
                current_time = time.time()
                led_sequence.append((state, current_time))

                if previous_led:
                    expected = "OFF" if previous_led[0] == "ON" else "ON"
                    if state != expected:
                        led_pattern_valid = False
                        log_lines.append(f"Pattern Error: expected {expected}, got {state}")

                    interval = current_time - previous_led[1]
                    if not first_led_interval_skipped and previous_led[0] == "ON" and state == "OFF":
                        first_led_interval_skipped = True
                        log_lines.append(f"Skipping first ON→OFF interval: {interval:.2f}s")
                    else:
                        if abs(interval - DELAY_EXPECTED) > TIME_TOLERANCE:
                            led_timing_valid = False
                            log_lines.append(f"Timing Error: {previous_led[0]} → {state} = {interval:.2f}s")
                        else:
                            log_lines.append(f"Interval OK: {previous_led[0]} → {state} = {interval:.2f}s")
                previous_led = (state, current_time)

    ser.close()
except Exception as e:
    log_lines.append(f"Serial Error: {str(e)}")

# Final result
test_passed = all([firmware_found, firmware_correct, firmware_first, led_pattern_valid, led_timing_valid])

# Styles
styles = """
<style>
body { font-family: Arial; padding: 20px; }
h1 { color: #2E86C1; }
.pass { color: green; font-weight: bold; }
.fail { color: red; font-weight: bold; }
table { border-collapse: collapse; width: 90%; margin-top: 10px; }
td, th { border: 1px solid #ccc; padding: 8px; text-align: center; }
th { background-color: #eee; }
pre { background: #f9f9f9; padding: 10px; border: 1px solid #ccc; }
a { text-decoration: none; color: #007bff; }
</style>
"""

# LED table
led_rows = ""
for i, (state, ts) in enumerate(led_sequence):
    readable = datetime.fromtimestamp(ts).strftime("%H:%M:%S")
    led_rows += f"<tr><td>{i+1}</td><td>{state}</td><td>{readable}</td></tr>"

# Write index.html (summary)
with open(f"{output_folder}/index.html", "w") as f:
    f.write(f"""
<!DOCTYPE html><html><head><title>Test Summary</title>{styles}</head><body>
<h1>Test Summary</h1>
<p><strong>Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
<h2>Overall Result: <span class="{ 'pass' if test_passed else 'fail' }">{'PASSED' if test_passed else 'FAILED'}</span></h2>
<table>
<tr><th>Test</th><th>Status</th><th>Details</th></tr>
<tr><td>Firmware</td><td><span class="{ 'pass' if firmware_correct and firmware_first else 'fail' }">{firmware_correct and firmware_first}</span></td><td><a href="firmware_details.html" target="_blank">View</a></td></tr>
<tr><td>LED</td><td><span class="{ 'pass' if led_pattern_valid and led_timing_valid else 'fail' }">{led_pattern_valid and led_timing_valid}</span></td><td><a href="led_details.html" target="_blank">View</a></td></tr>
</table></body></html>
""")

# Write firmware_details.html
with open(f"{output_folder}/firmware_details.html", "w") as f:
    f.write(f"""
<!DOCTYPE html><html><head><title>Firmware Details</title>{styles}</head><body>
<a href="index.html">← Back to Summary</a>
<h1>Firmware Check</h1>
<ul>
<li>Firmware Found: <span class="{ 'pass' if firmware_found else 'fail' }">{firmware_found}</span></li>
<li>Version Correct: <span class="{ 'pass' if firmware_correct else 'fail' }">{firmware_correct}</span></li>
<li>First Line: <span class="{ 'pass' if firmware_first else 'fail' }">{firmware_first}</span></li>
</ul>
<h2>Logs</h2>
<pre>{'\n'.join(log_lines)}</pre>
</body></html>
""")

# Write led_details.html
with open(f"{output_folder}/led_details.html", "w") as f:
    f.write(f"""
<!DOCTYPE html><html><head><title>LED Details</title>{styles}</head><body>
<a href="index.html">← Back to Summary</a>
<h1>LED Test</h1>
<ul>
<li>Pattern Valid: <span class="{ 'pass' if led_pattern_valid else 'fail' }">{led_pattern_valid}</span></li>
<li>Timing Valid: <span class="{ 'pass' if led_timing_valid else 'fail' }">{led_timing_valid}</span></li>
<li>Total Events: {len(led_sequence)}</li>
</ul>
<h2>LED Sequence</h2>
<table><tr><th>#</th><th>State</th><th>Time</th></tr>{led_rows}</table>
<h2>Logs</h2>
<pre>{'\n'.join(log_lines)}</pre>
</body></html>
""")

# Open the index.html
webbrowser.open(f"file://{os.path.abspath(output_folder)}/index.html")
