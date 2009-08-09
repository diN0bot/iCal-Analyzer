
from classes import *

import os
import re
from datetime import datetime

class Reader(object):
    calendar_uid_map = {}
    event_uid_map = {}
    group_uid_map = {}
    
    current_calendar = None
    
    @classmethod
    def read_calendars(klass, calendars_dir):
        items = {'events':[], 'calendars':[]}
        os.path.walk( calendars_dir,
                      klass.callback,
                      items )
        
        print "OK< NOW PRINT events"
        for e in items['events']:
            print e
        print len(items['events'])
        for e in items['calendars']:
            print e
        
        return items


    @classmethod
    def callback(klass, arg, dirname, fnames):
        for fname in fnames:
            full_fname = dirname + '/' + fname
            print full_fname
            if os.path.isfile(full_fname) and fname[-4:] == ".ics":
                event = klass.read_event_file(full_fname)
                print "  >>> EVENT ", event
                arg['events'].append(event)
            elif dirname[-6:] == ".group" and fname == "Info.plist":
                pass
            elif dirname[-9:] == ".calendar" and fname == "Info.plist":
                calendar = klass.read_calendar_file(full_fname)
                klass.current_calendar = calendar
                print "  >>> CALENDAR ", calendar
                arg['calendars'].append(calendar)

    @classmethod
    def read_calendar_file(klass, fname):
        """
        <?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
        <plist version="1.0">
        <dict>
            <key>AlarmsDisabled</key>
            <false/>
            <key>Checked</key>
            <integer>1</integer>
            <key>Color</key>
            <string>#0252D4FF</string>
            <key>Editable</key>
            <true/>
            <key>Enabled</key>
            <true/>
            <key>Key</key>
            <string>416B94A2-1DF2-41DF-930B-AB5CF029D14D</string>
            <key>Order</key>
            <integer>6</integer>
            <key>Title</key>
            <string>play</string>
            <key>Type</key>
            <string>Local</string>
        </dict>
        </plist>
        """
        f = open(fname, 'r')
        found_title_key = False
        for line in f.readlines():
            if found_title_key:
                title = re.findall("<string>([^<]+)</string>", line)[0]
                return Calendar(title)
            if line.strip() == "<key>Title</key>":
                found_title_key = True
        f.close()
        return None

    @classmethod
    def read_event_file(klass, fname):
        """
        DTSTART;TZID=Europe/Berlin:20090804T230000
        
        BEGIN:VCALENDAR
        VERSION:2.0
        PRODID:-//Apple Inc.//iCal 3.0//EN
        CALSCALE:GREGORIAN
        BEGIN:VEVENT
        SEQUENCE:3
        TRANSP:OPAQUE
        UID:7AE01F84-F885-49B2-A35B-9CF73771B797
        DTSTART;TZID=US/Eastern:20090727T200000
        DTSTAMP:20090809T180349Z
        SUMMARY:TEST@
        CREATED:20090809T180331Z
        DTEND;TZID=US/Eastern:20090727T220000
        RRULE:FREQ=WEEKLY;INTERVAL=1
        END:VEVENT
        END:VCALENDAR
        """
        # only record key values whose keys exist in this dictionary.
        # use these dictionary values as self field names
        file_key_value_map = {'SUMMARY':'summary',
                              'DTSTART':'start',
                              'DTEND':'end',
                              'TZID':'tz'}

        event = Event()
        f = open(fname, 'r')
        for line in f.readlines():
            """
            every line should have this form:: 
                <key>:<value>
            where key is an expression of this form::
                <key_name>(;<sub_key_name>=<sub_value>)*
            and value is an expression of the same form but with different names::
                <value> | <sub_value_name>=<sub_value>;(<sub_value_name>=<sub_value>)+
            """
            """
                DTSTART;TZID=US/Eastern:20090727T200000
            yields
                self.start = datetime(20090727T200000)
                self.start_tz = US/Eastern
                
                RRULE:FREQ=WEEKLY;INTERVAL=1
            yeilds
                self.rrule =  {'freq':'weekly', 'interval'=1}
            """
            def smart_split(item_to_split, splitch):
                items = item_to_split.split(splitch)
                ret = []
                for item in items:
                    item = item.strip()
                    try:
                        #20090727T200000
                        item = datetime.strptime(item, "%Y%m%dT%H%M%S")
                    except ValueError:
                        pass
                    ret.append(item)
                return ret
            
            def smart_name(name):
                if name in file_key_value_map:
                    return file_key_value_map[name]
                else:
                    return name
            
            # parse the line
            key_value = smart_split(line, ':')
            if len(key_value) == 1:
                print "skipping line because ':' not found", key_value
                continue
            key = key_value[0]
            value = key_value[1]
            # find sub keys:: <key>;<subkey>=<subvalue>;...:<value>
            if isinstance(key, str) and ';' in key:
                sub_keys = smart_split(key, ';')
                key = sub_keys[0]
                sub_keys = sub_keys[1:]
            else:
                sub_keys = []
            # find sub values:: <key>:<va;<subkey>=<subvalue>;...:<value>
            if isinstance(value, str) and ';' in value and not '\;' in value:
                sub_values = smart_split(value, ';')
                value = None
            else:
                sub_values = []
            
            # now add properties to this event
            if key in file_key_value_map:
                # create sub value dictionary if necessary and set to values
                if sub_values:
                    value = {}
                    for sub_value in sub_values:
                        key_value = smart_split(sub_value, '=')
                        value[key_value[0].lower()] = key_value[1].lower()
                # set event.key = value 
                setattr(event, smart_name(key), value)
                # set sub key  properties if necessary
                if sub_keys:
                    for sub_key in sub_keys:
                        key_value = smart_split(sub_key, '=')
                        setattr(event,
                                "%s_%s" % (smart_name(key), smart_name(key_value[0])),
                                key_value[1])
        f.close()
        if klass.current_calendar:
            event.assign_calendar(klass.current_calendar)
        return event
