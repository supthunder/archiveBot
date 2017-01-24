import os
import time

# Run every 30 seconds
def main():
	while(True):
		os.system("python3 archive.py")
		time.sleep(30)
main()
