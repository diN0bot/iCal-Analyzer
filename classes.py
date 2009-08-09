"""
Simple iCal model: Groups, Calendars and Events.

@todo: add Week, Day, Month cross references. Maybe Forever, too. one class with type.
"""

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
    def __init__(self, name):
        self.name = name
        self.group = None
        self.events = []
    
    def add_event(self, event):
        """
        called by Event.add_calendar()
        """
        self.events.append(event)
    
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
    def __init__(self):
        """
        Instance fields are added using self.add_field().
        Expected fields are:
         * start (datetime)
         * end (datetime)
         * summary (string)
        """
        self.calendar = None
    
    def add_field(self, name, value):
        setattr(self, name, value)
        
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
        if hasattr(self, "start") and hasattr(self, "end"):
            #print "start", self.start, type(self.start)
            #print "end", self.end, type(self.end)
            return (self.end - self.start).seconds
        return 0

    def __str__(self):
        return "%s hours, %s" % (self.duration() / 3600, self.__dict__)
