
class Group(object):
    
    def __init__(self, name):
        self.name = name
        self.calendars = []
    
    def add_calendar(self, calendar):
        self.calendars.append(calendar)

class Calendar(object):
    
    def __init__(self, name):
        self.name = name
        self.group = None
        self.events = []
    
    def add_event(self, event):
        self.events.append(event)
    
    def add_group(self, group):
        self.group = group
        group.add_calendar(self)

    def __str__(self):
        return "%s (%s)" % (self.name, len(self.events))

class Event(object):
    
    def __init__(self):
        self.calendar = None
        
    def assign_calendar(self, calendar):
        self.calendar = calendar
        calendar.add_event(self)
    
    def duration(self):
        if hasattr(self, "start") and hasattr(self, "end"):
            #print "start", self.start, type(self.start)
            #print "end", self.end, type(self.end)
            return (self.end - self.start).seconds
        return 0

    def __str__(self):
        return "%s hours, %s" % (self.duration() / 3600, self.__dict__)
#@TODO add Week, Day, Month cross references. Maybe Forever, too. one class with type.