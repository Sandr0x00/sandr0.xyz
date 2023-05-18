import re
from datetime import datetime
import os

with open("access.log", "r") as f:
    log = f.read().splitlines()

files = {}

fmt = "%Y-%m"

now = datetime.now().strftime(fmt)
cur_month = None
cur_file = None

if not os.path.exists("logs"):
    os.mkdir("logs")

print(now)
for l in log:
    m = re.match(r"^.*\[(\d{2}/\w{3}/\d{4}:\d\d:\d\d:\d\d \+\d{4})\].*$", l)
    assert m
    date = datetime.strptime(m.group(1), "%d/%b/%Y:%H:%M:%S %z")
    month = date.strftime(fmt)


    if cur_month != month:
        if cur_file:
            cur_file.close()
        cur_month = month
        if cur_month == now:
            cur_file = open("access.log", "w")
        else:
            cur_file = open(f"logs/access.{month}.log", "w")

    cur_file.write(l)
    cur_file.write("\n")
