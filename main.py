"""
Reads in iCal files on your computer and outputs calendar statistics such as
average hours spent, minimum, maximum and total.
Will create a google chart image if pygooglechart is installed.
"""

import os

import reader, analyzer

CALENDARS_DIR = "/Users/lucy/Library/Calendars"

if __name__ == "__main__":
    # read calendar files into internal data structure
    data = reader.Reader.read_calendars(CALENDARS_DIR)
    # analyze data
    analyzer.Analyzer.print_totals(data, type='by_calendar', timeframe='forever')
    try:
        import pygooglechart
        analyzer.Analyzer.google_chart(data)
    except:
        print "\nPlease download pygooglechart to create charts\n    http://pygooglechart.slowchop.com/"
    