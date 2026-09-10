# Create one alert function per sensor buoy.
# Should print:
#   Buoy B1 offline
#   Buoy B2 offline
#   Buoy B3 offline
alerts = []
for buoy in ["B1", "B2", "B3"]:
    alerts.append(lambda buoy=buoy: f"Buoy {buoy} offline")

for alert in alerts:
    print(alert())
