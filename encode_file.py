import base64
import os

file_path = input("Enter file path: ").strip().strip('"')

if not os.path.exists(file_path):
    print("❌ File not found")
    exit()

with open(file_path, "rb") as f:
    encoded = base64.b64encode(f.read()).decode("utf-8")

print("\n✅ BASE64 OUTPUT:\n")
print(encoded)