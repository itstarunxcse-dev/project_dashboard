import os
import glob

# Find the file that looks like the overview file
files = glob.glob("0_*Overview.py")
for f in files:
    print(f"Found file: {f}")
    new_name = "0_Overview.py"
    try:
        os.rename(f, new_name)
        print(f"Renamed {f} to {new_name}")
    except Exception as e:
        print(f"Error renaming {f}: {e}")
