	#!/bin/sh

	for i in {1..100}; do
		nohup python3 ident_run.py & 
		echo "Running : $i"
	done

