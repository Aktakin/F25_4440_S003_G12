<<<<<<< HEAD:Misc/Israel Ogunseye/mini_mobsf_summary.py
import json
import os

# ----------------------------
# SETTINGS
# ----------------------------
JSON_PATH = r"C:\Users\fixer\isyyproject\mobsf_telegram_report\telegram_report.json"
OUTPUT_FOLDER = r"C:\Users\fixer\isyyproject\mobsf_telegram_report"

# Dangerous permissions list (can add more)
DANGEROUS_PERMISSIONS = [
    "ACCESS_BACKGROUND_LOCATION",
    "ACCESS_COARSE_LOCATION",
    "ACCESS_FINE_LOCATION",
    "SEND_SMS",
    "READ_SMS",
    "READ_CONTACTS",
    "WRITE_CONTACTS",
    "READ_CALENDAR",
    "WRITE_CALENDAR",
    "RECORD_AUDIO",
    "CAMERA"
]

# ----------------------------
# LOAD JSON REPORT
# ----------------------------
if not os.path.exists(JSON_PATH):
    print(f"JSON file not found: {JSON_PATH}")
    exit()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    report = json.load(f)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def check_dangerous_permissions(permissions_text):
    found = []
    for perm in DANGEROUS_PERMISSIONS:
        if perm in permissions_text:
            found.append(perm)
    return found

def extract_list(section_text):
    return [line.strip() for line in section_text.split("\n") if line.strip()]

# ----------------------------
# ANALYSIS
# ----------------------------
print("=== MobSF Mini Security Summary ===\n")

# File info
print("File Information:")
print(report.get("file_information", "N/A"), "\n")

# App info
print("App Information:")
print(report.get("app_information", "N/A"), "\n")

# Dangerous Permissions
permissions_text = report.get("permissions", "")
dangerous = check_dangerous_permissions(permissions_text)
if dangerous:
    print("⚠️ Dangerous Permissions Found:")
    for perm in dangerous:
        print(" -", perm)
else:
    print("No dangerous permissions found.")
print()

# Exported components
for section in ["exported_activities", "exported_services", "exported_receivers", "exported_providers"]:
    items = extract_list(report.get(section, ""))
    print(f"{section.replace('_', ' ').title()} ({len(items)}):")
    if items:
        for item in items:
            print(" -", item)
    else:
        print(" None found.")
    print()

# Optional: save summary to a text file
summary_file = os.path.join(OUTPUT_FOLDER, "telegram_mini_summary.txt")
with open(summary_file, "w", encoding="utf-8") as f:
    f.write("=== MobSF Mini Security Summary ===\n\n")
    f.write("File Information:\n" + report.get("file_information", "N/A") + "\n\n")
    f.write("App Information:\n" + report.get("app_information", "N/A") + "\n\n")
    f.write("Dangerous Permissions:\n" + ("\n".join(dangerous) if dangerous else "None") + "\n\n")
    for section in ["exported_activities", "exported_services", "exported_receivers", "exported_providers"]:
        items = extract_list(report.get(section, ""))
        f.write(f"{section.replace('_', ' ').title()} ({len(items)}):\n")
        f.write("\n".join(items) if items else "None")
        f.write("\n\n")

print(f"Mini summary saved to: {summary_file}")
=======
import json
import os

# ----------------------------
# SETTINGS
# ----------------------------
JSON_PATH = r"C:\Users\fixer\isyyproject\mobsf_telegram_report\telegram_report.json"
OUTPUT_FOLDER = r"C:\Users\fixer\isyyproject\mobsf_telegram_report"

# Dangerous permissions list (can add more)
DANGEROUS_PERMISSIONS = [
    "ACCESS_BACKGROUND_LOCATION",
    "ACCESS_COARSE_LOCATION",
    "ACCESS_FINE_LOCATION",
    "SEND_SMS",
    "READ_SMS",
    "READ_CONTACTS",
    "WRITE_CONTACTS",
    "READ_CALENDAR",
    "WRITE_CALENDAR",
    "RECORD_AUDIO",
    "CAMERA"
]

# ----------------------------
# LOAD JSON REPORT
# ----------------------------
if not os.path.exists(JSON_PATH):
    print(f"JSON file not found: {JSON_PATH}")
    exit()

with open(JSON_PATH, "r", encoding="utf-8") as f:
    report = json.load(f)

# ----------------------------
# HELPER FUNCTIONS
# ----------------------------
def check_dangerous_permissions(permissions_text):
    found = []
    for perm in DANGEROUS_PERMISSIONS:
        if perm in permissions_text:
            found.append(perm)
    return found

def extract_list(section_text):
    return [line.strip() for line in section_text.split("\n") if line.strip()]

# ----------------------------
# ANALYSIS
# ----------------------------
print("=== MobSF Mini Security Summary ===\n")

# File info
print("File Information:")
print(report.get("file_information", "N/A"), "\n")

# App info
print("App Information:")
print(report.get("app_information", "N/A"), "\n")

# Dangerous Permissions
permissions_text = report.get("permissions", "")
dangerous = check_dangerous_permissions(permissions_text)
if dangerous:
    print("⚠️ Dangerous Permissions Found:")
    for perm in dangerous:
        print(" -", perm)
else:
    print("No dangerous permissions found.")
print()

# Exported components
for section in ["exported_activities", "exported_services", "exported_receivers", "exported_providers"]:
    items = extract_list(report.get(section, ""))
    print(f"{section.replace('_', ' ').title()} ({len(items)}):")
    if items:
        for item in items:
            print(" -", item)
    else:
        print(" None found.")
    print()

# Optional: save summary to a text file
summary_file = os.path.join(OUTPUT_FOLDER, "telegram_mini_summary.txt")
with open(summary_file, "w", encoding="utf-8") as f:
    f.write("=== MobSF Mini Security Summary ===\n\n")
    f.write("File Information:\n" + report.get("file_information", "N/A") + "\n\n")
    f.write("App Information:\n" + report.get("app_information", "N/A") + "\n\n")
    f.write("Dangerous Permissions:\n" + ("\n".join(dangerous) if dangerous else "None") + "\n\n")
    for section in ["exported_activities", "exported_services", "exported_receivers", "exported_providers"]:
        items = extract_list(report.get(section, ""))
        f.write(f"{section.replace('_', ' ').title()} ({len(items)}):\n")
        f.write("\n".join(items) if items else "None")
        f.write("\n\n")

print(f"Mini summary saved to: {summary_file}")
>>>>>>> 5348b93 (Move all MobSF Telegram analysis files into Israel Ogunseye folder):Israel Ogunseye/mini_mobsf_summary.py
