# Average sea ice thickness over 7 days (cm).
# Should print: 150.0
thickness = [140, 145, 150, 150, 155, 160, 150]
total = 0
for i in range(1, len(thickness)):
    total += thickness[i]
print(total / len(thickness))
