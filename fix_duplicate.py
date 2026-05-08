import os

app_file = r"c:\Users\Lenovo\Desktop\KhetIQ\frontend\src\App.jsx"
with open(app_file, "r", encoding="utf-8") as f:
    lines = f.readlines()

# The redundant one is the one in BuyerPortal that uses farmer.id (accidentally inserted)
# Or just find the one between line 1442 and 1452 (1-indexed)
# 0-indexed: 1441 to 1451

new_lines = lines[:1441] + lines[1452:]

with open(app_file, "w", encoding="utf-8") as f:
    f.writelines(new_lines)

print("Redundant declaration removed")
