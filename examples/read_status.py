"""Example: read battery box status."""

from battery_box_sdk import BatteryBoxClient, BatteryBoxError

with BatteryBoxClient(port="/dev/ttyLP0", baudrate=115200) as client:
    try:
        status = client.read_status()
    except BatteryBoxError as e:
        print(f"Error: {e}")
        raise SystemExit(1) from e

print(f"IC temperature: {status.charger.ic_temperature_c:.1f} °C")
print(f"Battery A SOC:  {status.battery_a.soc_percent:.1f} %")
print(f"Battery A SOH:  {status.battery_a.soh.estimated_percent:.1f} %")
print(f"Battery B SOC:  {status.battery_b.soc_percent:.1f} %")
print(f"Battery B SOH:  {status.battery_b.soh.estimated_percent:.1f} %")
print()
print("Alarms:")
print(f"  LTC4015 error:        {status.alarms.ic4015.error}")
print(f"  LTC4015 temp > 95°C:  {status.alarms.ic4015.temp_over_95c}")
print(f"  Battery A temp > 65°C:{status.alarms.battery.a_temp_over_65c}")
print()
print("Protections:")
print(f"  Pack over-voltage:    {status.protections.pack_over_voltage}")
print(f"  Pack under-voltage:   {status.protections.pack_under_voltage}")
