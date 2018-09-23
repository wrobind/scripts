#!/usr/bin/env python3

# convert VCF contacts file to CSV format file, listing labels as first line of CSV

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

note_contribution = re.compile(r'\b(\d{4}-\d{2}-\d{2}\s+#\d+\s\$[0-9,.]+\b)+')


with open(infile) as inf:
	contacts = vobject.readComponents(inf.read())
	inf.close()


fieldnames = ['ST', 'DIST', 'LEVEL', 'SAFE', 'CONTRIBS', 'FAMILY', 'GIVEN', 'FULLNAME', 'NOTE', 'DETAIL', 'ADDRESS', 'EMAIL', 'URL']

records = []
for contact in contacts:
	if 'fn' not in contact.contents:
		continue

	record = {}
	record['LEVEL'] = 'UNKN'

	if 'org' in contact.contents:
		m = org_federal_seat.match(contact.org.value[0])
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
		record['DETAIL'] = ';'.join(contact.org.value)

	if 'note' in contact.contents:
		if 'SAFE' not in record or record['SAFE'] == 'U':
			m = seat_safety.search(contact.note.value)
			if m is not None:
				if m.group(2) is not None:
					record['SAFE'] = m.group(2).upper()
				else:
					record['SAFE'] = 'U'
		m = note_contribution.findall(contact.note.value)
		if m is not None:
			record['CONTRIBS'] = '@'.join(m)
		record['NOTE'] = contact.note.value


	if 'n' in contact.contents:
		record['GIVEN'] = contact.n.value.given
		record['FAMILY'] = contact.n.value.family
		record['FULLNAME'] = contact.n.value
	if 'adr' in contact.contents:
		record['ADDRESS'] = contact.adr.value
	# if 'email' in contact.contents:
		# record['EMAIL'] = contact.email.value
	if 'url' in contact.contents:
		record['URL'] = contact.url.value

	records.append(record)	


with open(outfile, 'w', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()
	writer.writerows(records)
	csvfile.close()
	

