#!/bin/bash

for i in *
do
	name=$(echo $i| cut -d'.' -f1)
	dot -Tpdf "${name}" -o "${name}.pdf"
	rm "${name}.dot"
done