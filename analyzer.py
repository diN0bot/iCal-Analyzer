"""
Compute and print calendar statistics.
"""

from __future__ import division
from math import ceil
import datetime

from classes import TimePeriod

import pygooglechart

class Analyzer(object):
    
    @classmethod
    def cross_reference_times(klass, data):
        for calendar in data['calendars']:
            if calendar.name == 'sleep':
                ordered_events = sorted(calendar.events)
                prev_event = None
                for event in ordered_events:
                    if prev_event:
                        TimePeriod.get_or_create(start=prev_event.end,
                                                 end=event.end)
                    else:
                        # first sleep
                        earlier = datetime.datetime(event.start.year,
                                                    event.start.month,
                                                    event.start.day-1)
                        TimePeriod.get_or_create(start=earlier,
                                                 end=event.end)
                    prev_event = event
                    if event == ordered_events[-1]:
                        # last sleep
                        later = datetime.datetime(event.end.year,
                                                  event.end.month,
                                                  event.end.day+1)
                        TimePeriod.get_or_create(start=event.end,
                                                 end=later)
        
        for event in data['events']:
            #if event.calendar.name != 'sleep':
            tp = TimePeriod.get_containing_time_period(event.start)
            if not tp:
                print "no time period contains this event. if not a first day event, then this is a problem", event
            else:
                event.assign_timeperiod(tp)
            
    
    
        """
        start_of_day = datetime.datetime(event.get_field('start').year,
                                         event.get_field('start').month,
                                         event.get_field('start').day,
                                         0, 0, 0)
        end_of_day = datetime.datetime(event.get_field('start').year,
                                       event.get_field('start').month,
                                       event.get_field('start').day,
                                       23, 59, 59)
        time_period = TimePeriod.get_or_create(start_of_day, end_of_day)
        time_period.add_event(event)
        if not time_period in self.events_by_time_period:
            self.events_by_time_period[time_period] = []
        self.events_by_time_period[time_period].append(event)
        """
    
    @classmethod
    def print_totals(klass, data, type='by_calendar', timeframe='forever'):
        """
        Iterates over each Calendar and prints to console:
             min, max, avg, count and total hours.
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
                duration = event.duration
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
        print MAX/3600
        
    @classmethod
    def google_chart(klass, data):
        """
        Creates a google chart called 'chart.png'
        """
        colors = []
        names = []
        lines = []
        for calendar in sorted(data['calendars']):
            colors.append(calendar.color)
            names.append(calendar.name)
            line = []
            for tp,events in calendar.ordered_time_periods():
                sum = 0
                for event in events:
                    sum += event.duration
                line.append(sum/3600)
            lines.append(line)
        #names.reverse()
        #colors.reverse()
        
        max_y = 0
        y_labels = []
        for (start, tp) in TimePeriod.get_ordered_periods():
            y_labels.append(start.strftime("%a %d"))#"%s/%s" % (start.month, start.day))
            tp_sum = 0
            for event in tp.events:
                tp_sum += event.duration
            if tp_sum/3600 > max_y:
                max_y = tp_sum/3600
        max_y = ceil(max_y)

        chart = pygooglechart.StackedVerticalBarChart(1000,
                                                      300,
                                                      y_range=[0, max_y],
                                                      legend=names,
                                                      colours=colors)
                                #colours=['000000']*len(data['calendars']),
                                #colours_within_series=colors)
                    
        for line in lines:
            chart.add_data(line)
        
        # Last value is the lowest in the Y axis.
        #chart.add_data([0] * 2)
          
        def factor(n):
            """
            from: http://blog.dhananjaynene.com/2009/01/2009-is-not-a-prime-number-a-python-program-to-compute-factors/ 
            Get the factors for a number 
            Not optimised for tail recursion 
            """  
            if n == 1: return [1]  
            i = 2  
            limit = n**0.5  
            while i <= limit:  
                if n % i == 0:  
                    ret = factor(n/i)  
                    ret.append(i)  
                    return ret  
                i += 1  
            return [n] 
        # Some axis data
        
        t = ['']
        factors = factor(max_y)
        if factors:
            tt = factors[0]
        else:
            tt = max_y
        print tt
        for i in range(int(tt)):
            t.append(max_y/tt*(i+1))
        chart.set_axis_labels(pygooglechart.Axis.LEFT, t)
        chart.set_axis_labels(pygooglechart.Axis.BOTTOM, y_labels)
        
        chart.set_bar_width(50)
        
        chart.download('chart.png')
   