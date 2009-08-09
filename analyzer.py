from __future__ import division

class Analyzer(object):
    
    @classmethod
    def print_totals(klass, data, type='by_calendar', timeframe='forever'):
        """
        --- PD ------------------
          avg:   6    /d:  6.2
          min:   2    /d:  4.0
          max:   4    /d: 11.0
        total:  66
        """
        for calendar in data['calendars']:
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
            