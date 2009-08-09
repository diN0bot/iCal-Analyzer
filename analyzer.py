"""
Compute and print calendar statistics.
"""

from __future__ import division

class Analyzer(object):
    
    @classmethod
    def print_totals(klass, data, type='by_calendar', timeframe='forever'):
        """
        Iterates over each Calendar and prints to console the following:
        ---- chores ------------------------------
        sum: 4.0
        cnt: 8
        avg: 0.5
        min: 0.0
        max: 1.5
        
        cnt = count, sum is the total.
        all amounts are in hours
        """
        for calendar in data['calendars']:
            print
            print '-'*4, calendar.name, '-'*30
            # in hours
            sum = 0
            min = 999999
            max = 0
            for event in calendar.events:
                duration = event.duration()
                sum += duration
                if duration < min:
                    min = duration
                if duration > max:
                     max = duration
            print "sum:", sum/3600
            print "cnt:", len(calendar.events)
            print "avg:", sum/3600/len(calendar.events)
            print "min:", min/3600
            print "max:", max/3600
            