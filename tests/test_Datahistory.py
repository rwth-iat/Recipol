import csv
import time
import os.path

filename = f"Datahistory\\log_{time.strftime('%d-%m-%Y_%H-%M-%S')}"
header = "This is a header"
flag = True
# try: 
#     with open(filename, 'r', newline='') as csvfile:
#         reader = csv.reader(csvfile)
# except FileNotFoundError:
for i in range(5):
    with open(filename, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if flag == True:
            writer.writerow(header)
            flag = False
        writer.writerow("Hello")