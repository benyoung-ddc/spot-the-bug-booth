# 3x3 grid of surveillance sectors. 0 = not scanned, 1 = scanned.
# Mark only the north-west sector (row 0, col 0) as scanned.
# Should print: Scanned sectors: 1
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 1
total = sum(sum(row) for row in grid)
print("Scanned sectors:", total)
