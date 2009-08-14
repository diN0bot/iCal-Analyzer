"""
Simple iCal model: Groups, Calendars and Events.

@todo: add Week, Day, Month cross references. Maybe Forever, too. one class with type.
"""

import datetime

def _sort_dict_by_key(d, reverse=False):
    """ proposed in PEP 265, using  the itemgetter """  
    return sorted(d.iteritems(), key=itemgetter(0), reverse=True)  

class Group(object):
    """
    Corresponds to iCal group of calendars
    """
    def __init__(self, name):
        self.name = name
        self.calendars = []
    
    def add_calendar(self, calendar):
        """
        called by Calendar.add_group()
        """
        self.calendars.append(calendar)

class Calendar(object):
    """
    Corresponds to iCal calendar
    """
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.group = None
        self.events = []
        self.events_by_time_period = {}
        
    def ordered_time_periods(self):
        ret = []
        for start in sorted(TimePeriod.All_Periods):
            tp = TimePeriod.All_Periods[start]
            if tp in self.events_by_time_period:
                ret.append( (tp, self.events_by_time_period[tp]) )
            else:
                ret.append( (tp, []) ) 
        return ret
        
    def add_event(self, event):
        """
        called by Event initializer
        """
        self.events.append(event)
    
    def add_event_with_time_period(self, event, time_period):
        if not time_period in self.events_by_time_period:
            self.events_by_time_period[time_period] = []
        self.events_by_time_period[time_period].append(event)
    
    def add_group(self, group):
        """
        calls Group.add_calendar()
        """
        self.group = group
        group.add_calendar(self)

    def __str__(self):
        return "%s (%s)" % (self.name, len(self.events))

class Event(object):
    """
    Corresponds to iCal event
    
    @todo: handle re-occurring events
    """
    
    def __init__(self, start, end, summary, calendar):
        """
        Instance fields are added using self.add_field().
        Expected fields are:
         * start (datetime)
         * end (datetime)
         * summary (string)
        """
        self.start = start
        self.end = end
        self.summary = summary
        self.calendar = calendar
        if self.calendar:
            calendar.add_event(self)
        self.time_period = None
        
        if self.end and self.start:
            self.duration = (self.end - self.start).seconds
        else:
            self.duration = 0
        
    #def __cmp__(self, x):
    #    return self.start < x.start
        
    def assign_timeperiod(self, time_period):
        self.time_period = time_period
        self.time_period.add_event(self)
        if self.calendar:
            self.calendar.add_event_with_time_period(self, time_period)

    def __str__(self):
        return "%s hrs (%s --- %s) %s" % (self.duration / 3600, self.start, self.end, self.calendar)

class TimePeriod(object):
    
    #### {start: [inst, inst, ...]}
    # {start: inst, }
    All_Periods = {}
    
    @classmethod
    def get_containing_time_period(klass, start):
        for s in klass.All_Periods:
            tp = klass.All_Periods[s]
            if start >= tp.start and start <= tp.end:
                return tp
        return None
    
    @classmethod
    def get_or_create(klass, start, end):
        if not start in klass.All_Periods:
            tp = TimePeriod(start, end)
            klass.All_Periods[start] = tp
        return klass.All_Periods[start]

    @classmethod
    def get_ordered_periods(klass):
        ret = []
        for tp in sorted(klass.All_Periods):
            ret.append( (tp, klass.All_Periods[tp]) )
        return ret
    
    def __init__(self, start, end):
        self.start = start
        self.end = end
        self.events = []
    
    def add_event(self, event):
        # called by Calendar
        self.events.append(event)

    def __str__(self):
        return "%s --- %s" % (self.start, self.end)