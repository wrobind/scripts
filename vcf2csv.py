#!/usr/bin/env python3

# convert VCF contacts file to CSV format file, listing labels as first line of CSV

import collections
import re
import vobject
import csv

# for development purposes, static file name

infile = 'Nelson2018-08.vcf'
outfile = 'Nelson2018-08.csv'

# political taxonomy

states = ['IA', 'KS', 'UT', 'VA', 'NC', 'NE', 'SD', 'AL', 'ID', 'FM', 'DE', 'AK', 'CT', 'PR', 'NM', 'MS', 'PW', 'CO', 'NJ', 'FL', 'MN', 'VI', 'NV', 'AZ', 'WI', 'ND', 'PA', 'OK', 'KY', 'RI', 'NH', 'MO', 'ME', 'VT', 'GA', 'GU', 'AS', 'NY', 'CA', 'HI', 'IL', 'TN', 'MA', 'OH', 'MD', 'MI', 'WY', 'WA', 'OR', 'MH', 'SC', 'IN', 'LA', 'MP', 'DC', 'MT', 'AR', 'WV', 'TX']

org_federal_seat = re.compile(r'(' + '|'.join(states) + r')[ -]+(\d+|S|G|AG)+', re.IGNORECASE)
org_state_seat = re.compile(r'(' + '|'.join(states) + r') ([hs]-\d+)', re.IGNORECASE)
seat_safety = re.compile(r'(safe)([DR])?\b', re.IGNORECASE)

pat_date = r'^(.*\b\d{4}[/-]\d{1,2}[/-]\d{1,2}.*?)$'
dated_line = re.compile(pat_date, re.IGNORECASE|re.MULTILINE)


fieldnames = ['ST', 'DIST', 'LEVEL', 'SAFE', 'DONATIONS', 'FAMILY', 'GIVEN', 'COMPANY', 'NOTE', 'ADDRESS']

fieldcounts = collections.Counter(fieldnames)

records = []
with open(infile, 'r') as inf:
	contacts = vobject.readComponents(inf.read())

for contact in contacts:
	# first VCard in Apple AB export has no Formatted Name
	#   and is not a contact
	if 'fn' not in contact.contents:
		continue

	record = {}
	record['LEVEL'] = 'UNKN'

	# Family and given names are in the 'N' field of the contact card
	if 'n' in contact.contents:
		record['GIVEN'] = contact.n.value.given
		record['FAMILY'] = contact.n.value.family

	if 'note' in contact.contents:
		record['NOTE'] = contact.note.value

	if 'adr' in contact.contents:
		record['ADDRESS'] = contact.adr.value

	if 'org' in contact.contents:
		record['COMPANY'] = contact.org.value[0]
		m = org_federal_seat.match(record['COMPANY'])
		if m is not None:
			record['LEVEL'] = 'FEDERAL'
			record['ST'] = m.group(1).upper()
			record['DIST'] = m.group(2).upper()
		else:
			m = org_state_seat.match(contact.org.value[0])
			if m is not None:
				record['LEVEL'] = 'STATE'
				record['ST'] = m.group(1).upper()
				record['DIST'] = m.group(2).upper()
		m = seat_safety.search(contact.org.value[0])
		if m is not None:
			if m.group(2) is not None:
				record['SAFE'] = m.group(2).upper()
			else:
				record['SAFE'] = 'U'

	if 'note' in contact.contents:
		if 'SAFE' not in record or record['SAFE'] == 'U':
			m = seat_safety.search(contact.note.value)
			if m is not None:
				if m.group(2) is not None:
					record['SAFE'] = m.group(2).upper()
				else:
					record['SAFE'] = 'U'
		checks = dated_line.findall(contact.note.value)
		if checks is not None:
			record['DONATIONS'] = '\r'.join(checks)

	records.append(record)
	for f in fieldnames:
		if f in record:
			fieldcounts[f] += 1

records.append(fieldcounts)

with open(outfile, 'w', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()
	writer.writerows(records)
	csvfile.close()
	

