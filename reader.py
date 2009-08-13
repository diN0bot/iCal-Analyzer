"""
Parses iCal files into Event, Calendar and Group data structures

@todo:
 * handle timezones
 * handle multi-line summaries (add to summary as encounter more lines?)
 * populate groups
"""

from classes import *

import os
import re
from datetime import datetime

DEBUG = False

class Reader(object):
    # set whenever a calender folder is encountered.
    # used when reading event files to know which calendar they are for 
    current_calendar = None
    
    @classmethod
    def read_calendars(klass, calendars_dir):
        """
        @param calendars_dir: root directory of calendar fields. Usually ~/Library/Calendars
        @return: dictionary {'events':[list of Events], 'calendars':[list of Calendars]}
        """
        items = {'events':[], 'calendars':[]}
        os.path.walk( calendars_dir,
                      klass.callback,
                      items )
        if DEBUG:
            for e in items['events']:
                print e
            print len(items['events'])
            for e in items['calendars']:
                print e

        return items


    @classmethod
    def callback(klass, arg, dirname, fnames):
        """
        method called by os.path.walk on each directory
        """
        for fname in fnames:
            full_fname = dirname + '/' + fname
            if DEBUG: print full_fname
        
            if os.path.isfile(full_fname) and fname[-4:] == ".ics":
                # EVENT FILE
                event = klass.read_event_file(full_fname)
                if DEBUG: print "  >>> EVENT ", event
                arg['events'].append(event)
                
            elif dirname[-6:] == ".group" and fname == "Info.plist":
                # GROUP FILE
                pass
            
            elif dirname[-9:] == ".calendar" and fname == "Info.plist":
                # CALENDAR FILE
                calendar = klass.read_calendar_file(full_fname)
                klass.current_calendar = calendar
                if DEBUG: print "  >>> CALENDAR ", calendar
                arg['calendars'].append(calendar)

    @classmethod
    def read_calendar_file(klass, fname):
        """
        Reads calendar info file, which looks like:
        
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
        
        @return: Calendar or None if could not extract calendar name
        """
        f = open(fname, 'r')
        found_title_key = False
        found_color_key = False
        title = None
        color = None
        for line in f.readlines():
            if found_title_key and not title:
                title = re.findall("<string>([^<]+)</string>", line)[0]
            if found_color_key and not color:
                color = re.findall("<string>#([^<]+)</string>", line)[0]
            if line.strip() == "<key>Title</key>":
                found_title_key = True
            if line.strip() == "<key>Color</key>":
                found_color_key = True
        return Calendar(title, color)
        f.close()
        return None

    @classmethod
    def read_event_file(klass, fname):
        """
        Reads calendar info file, which looks like:
        
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
        (( or if traveling...
        DTSTART;TZID=Europe/Berlin:20090804T230000
        ))
        RRULE:FREQ=WEEKLY;INTERVAL=1
        END:VEVENT
        END:VCALENDAR
        
        @return: Event
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
                event.add_field(smart_name(key), value)
                # set sub key  properties if necessary
                if sub_keys:
                    for sub_key in sub_keys:
                        key_value = smart_split(sub_key, '=')
                        event.add_field("%s_%s" % (smart_name(key), smart_name(key_value[0])),
                                        key_value[1])
        f.close()
        if klass.current_calendar:
            event.assign_calendar(klass.current_calendar)
        return event
