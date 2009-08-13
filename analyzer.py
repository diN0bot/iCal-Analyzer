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
        url = 'http://chart.apis.google.com/chart?chs=1000x300&cht=bvs&'
        url += 'chco='
        for calendar in data['calendars']:
            url += calendar.color
            if calendar != data['calendars'][-1]:
                url += ','
        url += '&chdl='
        for calendar in data['calendars']:
            url += calendar.name
            if calendar != data['calendars'][-1]:
                url += '|'
        url += '&chd=t:'
        MAX = 0
        for calendar in data['calendars']:
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
                if duration > MAX:
                    MAX = duration
                url += str(duration/3600)
                if event != calendar.events[-1]:
                    url += ','
            if calendar != data['calendars'][-1]:
                url += '|'
            print calendar.name, ' :: ', min/3600, "-", max/3600, '=', sum/3600, '    ', sum/3600/len(calendar.events), '(', len(calendar.events), ')'
        
        url += '&chma=30,30,30,30&chg=20,20,3,3&chxt=x,y&chxr=1,0,'
        url += str(MAX/3600)
        url += ',4'
        print url
            