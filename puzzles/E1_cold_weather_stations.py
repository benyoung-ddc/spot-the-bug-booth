# Count stations at or below -40 C.
# Should print: Stations at risk: 2
readings = {"Alert": -41, "Eureka": -38, "Resolute": -40, "Iqaluit": -25}
count = 0
for station, temp in readings.items():
    if temp < -40:
        count += 1
print("Stations at risk:", count)
