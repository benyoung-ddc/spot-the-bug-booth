# Remove friendly contacts from the radar list.
# Should print: ['unknown', 'unknown']
contacts = ["friendly", "friendly", "unknown", "friendly", "unknown"]
contacts = [c for c in contacts if c != "friendly"]
print(contacts)
