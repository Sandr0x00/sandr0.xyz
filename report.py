#!/usr/bin/env python3

import os
import subprocess
import re

done = []

for f in os.listdir("secured"):
    if (m := re.match(r"^report.(\d{4}-\d\d).html$", f)):
        done.append(m.group(1))

for f in os.listdir("logs"):
    if (m := re.match(r"^access.(\d{4}-\d\d).log$", f)):
        if m.group(1) not in done:
            subprocess.run(["goaccess", f"logs/access.{m.group(1)}.log", "-a", "-o", f"secured/report.{m.group(1)}.html"])
            print(f"report.{m.group(1)}.html written")
        else:
            print(f"report.{m.group(1)}.html already exists")


subprocess.run(["goaccess", "access.log", "-a", "-o", "secured/report.html"])
