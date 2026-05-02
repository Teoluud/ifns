import sys

import pandas as pd
from optparse import OptionParser


parser = OptionParser(usage='usage: %prog [options] tsv')
(opts, args) = parser.parse_args()
if len(args) == 0:
    sys.exit('Please provide a tsv file')
tsv_file = args[0]
df = pd.read_csv(tsv_file, sep='\t')
csv_file = tsv_file.strip('.txt') + '.csv'
df.to_csv(csv_file, index=False)