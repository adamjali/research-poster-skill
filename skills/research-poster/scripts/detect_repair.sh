#!/bin/bash
# detect_repair.sh <pptx> , opens a .pptx in PowerPoint, dismisses any "repaired and
# removed it" alert, and reports how many native chart objects SURVIVED the open.
# Use after building native charts: if a chart count drops, PowerPoint stripped it
# (usually because a chart set a data-label POSITION, the known repair trigger).
SRC="$1"
osascript -e 'tell application "Microsoft PowerPoint" to quit saving no' 2>/dev/null; sleep 1
pkill -9 -x "Microsoft PowerPoint" 2>/dev/null; sleep 1
osascript <<OSA 2>&1 | tail -1
with timeout of 90 seconds
	tell application "Microsoft PowerPoint" to launch
	delay 2
	tell application "Microsoft PowerPoint" to open POSIX file "$SRC"
	delay 4
	tell application "System Events" to tell process "Microsoft PowerPoint"
		set alerted to false
		repeat 5 times
			try
				if exists (button "OK" of window 1) then
					set alerted to true
					click button "OK" of window 1
				end if
			end try
			delay 0.6
		end repeat
	end tell
	set nchart to 0
	try
		tell application "Microsoft PowerPoint"
			repeat with sh in (shapes of slide 1 of active presentation)
				try
					if (has chart of sh) then set nchart to nchart + 1
				end try
			end repeat
			close active presentation saving no
		end tell
	end try
	return ("native charts surviving = " & nchart & "   repair alert fired = " & alerted)
end timeout
OSA
osascript -e 'tell application "Microsoft PowerPoint" to quit saving no' 2>/dev/null; pkill -9 -x "Microsoft PowerPoint" 2>/dev/null
