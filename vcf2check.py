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
date_pattern = re.compile(pat_date, re.IGNORECASE|re.MULTILINE)


fieldnames = ['contacts_check', 'contacts_amount', 'contacts_donations', 'FAMILY', 'ST', 'DIST']

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

	# Family and given names are in the 'N' field of the contact card
	if 'n' in contact.contents:
		record['FAMILY'] = contact.n.value.family


	if 'org' in contact.contents:
		m = org_federal_seat.match(contact.org.value[0])
		if m is not None:
			record['ST'] = m.group(1).upper()
			record['DIST'] = m.group(2).upper()
		else:
			m = org_state_seat.match(contact.org.value[0])
			if m is not None:
				record['ST'] = m.group(1).upper()
				record['DIST'] = m.group(2).upper()

	if 'note' in contact.contents:
		date_items = date_pattern.findall(contact.note.value)
		if date_items is not None:
			record['contacts_donations'] = '\r'.join(date_items)
			for date_item in date_items[1:]:
				check = re.search(r'(#?|[^/-])(\d{4})[^/-]', date_item)
				if check is not None:
					record['contacts_check'] = check[2]
				amount = re.search(r'-?\$[0-9,.]+\b', date_item)
				if amount is not None:
					record['contacts_amount'] = amount[0]

	records.append(record)


with open(outfile, 'w', newline='') as csvfile:
	writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

	writer.writeheader()
	writer.writerows(records)
	csvfile.close()
	

