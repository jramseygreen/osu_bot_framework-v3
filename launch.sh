#! /bin/bash
status=False
type -P python3 >/dev/null 2>&1 && status=True
if $status==False;
	apt install python3 -y
fi
python3 main.py