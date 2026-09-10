# Remove friendly contacts from the radar list.
# Should print: ['unknown', 'unknown']
contacts = ["friendly", "friendly", "unknown", "friendly", "unknown"]
for c in contacts:
    if c == "friendly":
        contacts.remove(c)
print(contacts)
