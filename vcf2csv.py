#!/usr/bin/env python3

# convert VCF contacts file to CSV format file, listing labels as first line of CSV

import re
import vobject
import csv


states = ['IA', 'KS', 'UT', 'VA', 'NC', 'NE', 'SD', 'AL', 'ID', 'FM', 'DE', 'AK', 'CT', 'PR', 'NM', 'MS', 'PW', 'CO', 'NJ', 'FL', 'MN', 'VI', 'NV', 'AZ', 'WI', 'ND', 'PA', 'OK', 'KY', 'RI', 'NH', 'MO', 'ME', 'VT', 'GA', 'GU', 'AS', 'NY', 'CA', 'HI', 'IL', 'TN', 'MA', 'OH', 'MD', 'MI', 'WY', 'WA', 'OR', 'MH', 'SC', 'IN', 'LA', 'MP', 'DC', 'MT', 'AR', 'WV', 'TX']

fn_states = re.compile(r'(' + '|'.join(states) + r')\b' + r'[ -]?(\d+|[SG])', re.IGNORECASE)

# for development purposes, static file name

infile = 'Nelson2018-08.vcf'
outfile = 'Nelson2018-08.csv'

with open(infile) as inf:
	contacts = vobject.readComponents(inf.read())
	inf.close()

records = []
fieldnames = ['ST', 'DIST', 'FAMILY', 'GIVEN', 'FULLNAME', 'NOTE', 'ORG', 'ADDRESS', 'EMAIL', 'URL']

for contact in contacts:
	record = {'ST': '  ', 'DIST': '   ', 'FULLNAME': '       ' }
	if 'fn' in contact.contents:
		if 'x-abshowas' in contact.contents:
			# if "show as" company, not the candidate
			if contact.contents['x-abshowas'] == 'COMPANY':
				record['ORG'] = contact.fn.value
			else:
				record['FULLNAME'] = contact.fn.value
		# "FN" (Formattted Name) field in Helm's contact list is often state-district
		m = fn_states.match(contact.fn.value)
		if m is not None:
			record['ST'] = m.group(1)
			record['DIST'] = m.group(2)

	if 'n' in contact.contents:
		record['GIVEN'] = contact.n.value.given
		record['FAMILY'] = contact.n.value.family
		if 'fn' not in contact.contents:
			record['FULLNAME'] = contact.n.value
			


	if 'adr' in contact.contents:
		record['ADDRESS'] = contact.adr.value
	# if 'email' in contact.contents:
		# record['EMAIL'] = contact.email.value
	if 'note' in contact.contents:
		record['NOTE'] = contact.note.value
	if 'org' in contact.contents:
		record['ORG'] = contact.org.value
	if 'url' in contact.contents:
		record['URL'] = contact.url.value

	records.append(record)	


with open(outfile, 'w', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()
	writer.writerows(records)
	csvfile.close()
	

