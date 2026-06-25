"""Example: read all available battery box properties."""

from battery_box_sdk import BatteryBoxClient, BatteryBoxError

with BatteryBoxClient(port="/dev/ttyLP0", baudrate=115200) as client:
    try:
        status = client.read_status()
    except BatteryBoxError as e:
        print(f"Error: {e}")
        raise SystemExit(1) from e

# ── Quick summary ──────────────────────────────────────────────────────────────
print(f"has_alert: {status.has_alert}")
print()

# ── Charger ────────────────────────────────────────────────────────────────────
print("=== Charger ===")
print(f"  active_battery_slot:    {status.charger.active_battery_slot}")
print(f"  battery_a_present:      {status.charger.battery_a_present}")
print(f"  battery_b_present:      {status.charger.battery_b_present}")
print(f"  output_enable:          {status.charger.output_enable}")
print(f"  charging_voltage_v:     {status.charger.charging_voltage_v:.3f} V")
print(f"  charging_current_a:     {status.charger.charging_current_a:.3f} A")
print(f"  ic_temperature_c:       {status.charger.ic_temperature_c:.1f} °C")
print(f"  battery_a_voltage_v:    {status.charger.battery_a_voltage_v:.3f} V")
print(f"  battery_a_current_a:    {status.charger.battery_a_current_a:.3f} A")
print(f"  battery_b_voltage_v:    {status.charger.battery_b_voltage_v:.3f} V")
print(f"  battery_b_current_a:    {status.charger.battery_b_current_a:.3f} A")
print()

# ── Battery A ──────────────────────────────────────────────────────────────────
print("=== Battery A ===")
print(f"  battery_id:                  {status.battery_a.battery_id}")
print(f"  soc_percent:                 {status.battery_a.soc_percent:.1f} %")
print(f"  bat_total_voltage_v:         {status.battery_a.bat_total_voltage_v:.2f} V")
print(f"  full_charge_capacity_mah:    {status.battery_a.full_charge_capacity_mah} mAh")
print(f"  charging_count:              {status.battery_a.charging_count}")
print(f"  soh.estimated_percent:       {status.battery_a.soh.estimated_percent:.1f} %")
print(f"  soh.capacity_ratio_percent:  {status.battery_a.soh.capacity_ratio_percent:.1f} %")
print(f"  soh.cycle_count_soh_percent: {status.battery_a.soh.cycle_count_soh_percent:.1f} %")
print()

# ── Battery B ──────────────────────────────────────────────────────────────────
print("=== Battery B ===")
print(f"  battery_id:                  {status.battery_b.battery_id}")
print(f"  soc_percent:                 {status.battery_b.soc_percent:.1f} %")
print(f"  bat_total_voltage_v:         {status.battery_b.bat_total_voltage_v:.2f} V")
print(f"  full_charge_capacity_mah:    {status.battery_b.full_charge_capacity_mah} mAh")
print(f"  charging_count:              {status.battery_b.charging_count}")
print(f"  soh.estimated_percent:       {status.battery_b.soh.estimated_percent:.1f} %")
print(f"  soh.capacity_ratio_percent:  {status.battery_b.soh.capacity_ratio_percent:.1f} %")
print(f"  soh.cycle_count_soh_percent: {status.battery_b.soh.cycle_count_soh_percent:.1f} %")
print()

# ── Alarms ─────────────────────────────────────────────────────────────────────
print("=== Alarms ===")
print(f"  ic4015.temp_over_95c:               {status.alarms.ic4015.temp_over_95c}")
print(f"  ic4015.temp_over_105c:              {status.alarms.ic4015.temp_over_105c}")
print(f"  ic4015.error:                       {status.alarms.ic4015.error}")
print(f"  battery.a_temp_over_65c:            {status.alarms.battery.a_temp_over_65c}")
print(f"  battery.a_temp_over_75c:            {status.alarms.battery.a_temp_over_75c}")
print(f"  battery.b_temp_over_65c:            {status.alarms.battery.b_temp_over_65c}")
print(f"  battery.b_temp_over_75c:            {status.alarms.battery.b_temp_over_75c}")
print(f"  system.reboot_by_ic4015_error:      {status.alarms.system.reboot_by_ic4015_error}")
print(f"  system.reboot_by_uart_error:        {status.alarms.system.reboot_by_uart_error}")
print(f"  system.stop_by_ic4015_temp:         {status.alarms.system.stop_by_ic4015_temp}")
print(f"  system.stop_by_battery_a_temp:      {status.alarms.system.stop_by_battery_a_temp}")
print(f"  system.stop_by_battery_b_temp:      {status.alarms.system.stop_by_battery_b_temp}")
v = status.alarms.system.output_12v_disabled_by_uart
print(f"  system.output_12v_disabled_by_uart:    {v}")
v = status.alarms.system.output_12v_disabled_by_battery
print(f"  system.output_12v_disabled_by_battery: {v}")
print()

# ── Protections ────────────────────────────────────────────────────────────────
print("=== Protections ===")
print(f"  pack_over_voltage:   {status.protections.pack_over_voltage}")
print(f"  pack_under_voltage:  {status.protections.pack_under_voltage}")
