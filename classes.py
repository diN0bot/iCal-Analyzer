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
        called by Event.assign_calendar()
        cross references event with a time period
        """
        self.events.append(event)
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
    def __init__(self, start=None, end=None, summary=None, calendar=None):
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
        self.calendar = None
        if calendar:
            self.assign_calendar(calendar)
    
    def add_field(self, name, value):
        setattr(self, name, value)
        
    def get_field(self, name, default=None):
        return getattr(self, name, default)
        
    def assign_calendar(self, calendar):
        """
        calls Calendar.add_event()
        """
        self.calendar = calendar
        calendar.add_event(self)
    
    def duration(self):
        """
        returns duration of event
        """
        if self.get_field('end') and self.get_field('start'):
            return (self.get_field('end') - self.get_field('start')).seconds
        else:
            return 0

    def __str__(self):
        return "%s hours, %s" % (self.duration() / 3600, self.__dict__)

class TimePeriod(object):
    
    #### {start: [inst, inst, ...]}
    # {start: inst, }
    All_Periods = {}
    
    @classmethod
    def get_or_create(klass, start, end):
        if not start in klass.All_Periods:
            tp = TimePeriod(start, end)
            klass.All_Periods[start] = tp
        return klass.All_Periods[start]
        
        """
            for tp in klass.All_Periods[start]:
                print "----- end ------", end
                if end == tp.end:
                    return tp
                print "   make new one   !"
            tp = TimePeriod(start, end)
            klass.All_Periods[start].append(tp)
            return tp
        tp = TimePeriod(start, end)
        klass.All_Periods[start] = [tp]
        return tp
        """

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
        return "%s - %s" % (self.start, self.end)