#!/usr/bin/python3

__author__ = 'Matthew Leeds <mwl458@gmail.com>'

import sys
import json
from configparser import ConfigParser
from math import floor

class CompareYears():
    """
    Examine Transactee and Party data that may span multiple years.
    If both the name and address of a contributor match, add the unique id's 
    of each to the other under 'equivalent_ids'. If the name, office, and district 
    of a candidate match, do the same. For a PAC, a matching name is sufficient to 
    assume equality. This means we can identify PACs/Candidates/Contributors/etc. 
    across years. The modified transactee and party data is written back out to the disk.
    """

    def __init__(self, config_file):
        """Read the config, initialize constants and variables for parties/transactees"""
        self.config = ConfigParser()
        self.config.read(config_file)
        self.data_dir = self.config.get('COMPARE_YEARS', 'DATA_DIR')
        self.all_transactees = []
        self.transactees_set_lengths = {} # maps years to numbers of records
        self.all_parties = []
        self.parties_set_lengths = {} # maps years to numbers of records
        # define which fields must match for each record type to be considered equivalent
        self.field_comparisons = {'Transactee': ['name', 'address'],
                                  'Candidate': ['name', 'office', 'district'],
                                  'PAC': ['name']}
    
    def _load_file(self, filename):
        """Load JSON data from the given filename, returning the result"""
        with open(self.data_dir + filename) as f:
            data = json.load(f)
        print('>> Loaded ' + str(len(data)) + ' records from ' + filename)
        return data
    
    def load_data(self):
        self.all_transactees = self._load_file(self.config.get('GENERATE_TRANSACTEES', 'OUTFILE'))
        self.all_parties = self._load_file(self.config.get('GENERATE_PARTIES', 'OUTFILE'))
    
    def _sort_by_year(self, records):
        """
        Sort the records by filed_year and count the number of records in each year
        :returns: a tuple of the sorted records and a mapping from years to numbers of records
        """
        byYear = {}
        for record in records:
            if record['filed_year'] in byYear:
                byYear[record['filed_year']].append(record)
            else:
                byYear[record['filed_year']] = [record]
        years = list(byYear.keys())
        years.sort()
        combined = []
        setLengths = {}
        for year in years:
            setLengths[year] = len(byYear[year])
            combined += byYear[year]
        return (combined, setLengths)

    def sort_by_year(self):
        """Make calls to _sort_by_year for transactees and parties"""
        (self.all_transactees, self.transactees_set_lengths) = self._sort_by_year(self.all_transactees)
        (self.all_parties, self.parties_set_lengths) = self._sort_by_year(self.all_parties)
         
    def _compare_years(self, records, setLengths):
        """
        Iterate over records, looking for records from different years that refer to the same entity.
        When the fields defined in self.field_comparisons match, equivalency is assumed.
        This takes n^3 time to run.
        :returns: a tuple with the modified records and how many were modified
        """
        years = list(setLengths.keys())
        years.sort()
        numModified = 0
        lastIndex = -1 # end of previous year's dataset
        for year in years[:-1]:
            print('year='+year)
            yearStart = lastIndex + 1
            yearEnd = yearStart + setLengths[year] - 1
            for i in range(yearStart, yearEnd + 1):
                #percentProgress = ((i - yearStart) / (yearEnd - yearStart)) * 100
                #if percentProgress == floor(percentProgress): print(str(int(percentProgress)) + '% complete')
                originalRecord = records[i]
                if 'transactee_type' in originalRecord: originalRecordType = 'Transactee'
                if 'type' in originalRecord: originalRecordType = originalRecord['type']
                for j in range(yearEnd + 1, len(records)):
                    record = records[j]
                    if 'transactee_type' in record: recordType = 'Transactee'
                    if 'type' in record: recordType = record['type']
                    if recordType != originalRecordType: continue
                    compare = [record[field] == originalRecord[field] for field in self.field_comparisons[recordType]]
                    same = all(compare)
                    if same:
                        # Add the id of each to the equivalent_ids list of the other (if it's not already there)
                        if 'equivalent_ids' in originalRecord and record['id'] not in originalRecord['equivalent_ids']:
                            originalRecord['equivalent_ids'].append(record['id'])
                        elif 'equivalent_ids' not in originalRecord:
                            originalRecord['equivalent_ids'] = [record['id']]
                        if 'equivalent_ids' in record and originalRecord['id'] not in record['equivalent_ids']:
                            record['equivalent_ids'].append(originalRecord['id'])
                        elif 'equivalent_ids' not in record:
                            record['equivalent_ids'] = [originalRecord['id']]
                        numModified += 1
            lastIndex = yearEnd
        return (records, numModified)
        
    def compare_years(self):
        """Make calls to _compare_years for transactees and parties"""
        (self.all_transactees, transacteesModified) = self._compare_years(self.all_transactees, self.transactees_set_lengths)
        (self.all_parties, partiesModified) = self._compare_years(self.all_parties, self.parties_set_lengths)
        print('>> Modified ' + str(transacteesModified) + ' transactee records and ' + 
                               str(partiesModified) + ' party records')

    def _write_file(self, records, filename):
        pretty_print = self.config.getboolean('COMPARE_YEARS', 'PRETTY_PRINT')
        with open(self.data_dir + filename, 'w') as f:
            if pretty_print:
                json.dump(records, f, sort_keys=True, indent=4, separators=(',', ': '))
            else:
                json.dump(records, f)
        print('>> Wrote ' + str(len(records)) + ' records to ' + filename)

    def write_data(self):
        self._write_file(self.all_transactees, self.config.get('GENERATE_TRANSACTEES', 'OUTFILE'))
        self._write_file(self.all_parties, self.config.get('GENERATE_PARTIES', 'OUTFILE'))

def main():
    compareYears = CompareYears('config.ini')
    compareYears.load_data()
    compareYears.sort_by_year()
    compareYears.compare_years()
    compareYears.write_data()

if __name__=='__main__':
    main()
