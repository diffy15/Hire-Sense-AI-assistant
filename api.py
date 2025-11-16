import os

folder_path = '.'  # current directory (same as app.py)
files = os.listdir(folder_path)

print("Files in folder:")
for file in files:
    print(file)
