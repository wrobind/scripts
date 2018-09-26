#!/usr/bin/env python3

import csv
import re

infile = 'foo.csv'
outfile = 'bar.csv'

in_fieldnames = [ 'date', 'ignore', 'label', 'amount' ]
out_fieldnames = [ 'checkreport_number', 'checkreport_amount', 'checkreport_payee', 'checkreport_date' ]

records = []

with open(infile, newline = '') as csvfile:
	reader = csv.DictReader(csvfile, fieldnames=in_fieldnames)

	for row in reader:
		record = {}
		record['checkreport_date'] = row['date']
		record['checkreport_amount'] = row['amount']
		m = re.match(r'#0(\d{4})\b\s+(.*)$', row['label'])
		if m is not None:
			record['checkreport_number'] = m[1]
			record['checkreport_payee'] = m[2]
		records.append(record)

with open(outfile, 'w', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=out_fieldnames)
	writer.writeheader()
	writer.writerows(records)
