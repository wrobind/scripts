#!/usr/bin/env python3

# convert VCF contacts file to CSV format file, listing labels as first line of CSV

import vobject

# for development purposes, static file name

infile = 'Nelson2018-08.vcf'
outfile = 'Nelson2018-08.csv'

with open(infile) as inf:
	indata = inf.read()
	vcollection = vobject.readComponents(indata)
	vinstance = next(vcollection, None)
	while vinstance is not None:
		print(vinstance.contents)
		print('  separator  ')
		print(vinstance.contents['prodid'])
		print('  =======================================  ')
		#vinstance.prettyPrint()
		vinstance = next (vcollection, None)


