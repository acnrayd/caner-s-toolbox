# This script assigns specific tag on KSC for the device. 
# Can be used as "installation package" on Kaspersky Security Center. 
# Script should be run in the client device.
#######

@echo off
set command=klscflag -ssvset -pv klnagent -s KLNAG_SECTION_TAGS_INFO -n KLCONN_HOST_TAGS -sv "[\"assigned_by_task_4_selection\"]" -svt ARRAY_T -ss "|ss_type = \"SS_PRODINFO\";" -t d -tl 4
set path2klnag=C:\Program Files (x86)\Kaspersky Lab\NetworkAgent\
cd %path2klnag%
cmd.exe /c mklink cmdin64.exe "C:\Windows\System32\cmd.exe"
cmdin64.exe /c %command%
