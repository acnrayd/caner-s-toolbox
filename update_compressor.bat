# I wrote this script for one of my clients, who required to download, compress and transfer database updates of Kaspersky Security Center
# manually to another server, every single day...
# On KSC, this .bat file was configured to run after every successful database update.

set YYYY=%date:~10,4%
set GUN=%date:~4,2%
set AY=%date:~7,2%
set FILENAME=Guncelleme_Paketi-%GUN%%AY%%YYYY%

set KAYNAK_PATH="C:\ProgramData\KasperskyLab\adminkit\1093\.working\share\Updates"
set HEDEF_PATH="C:\ProgramData\KasperskyLab\adminkit\1093\.working\share\%FILENAME%.zip"

powershell -Command "& {Compress-Archive -Path %KAYNAK_PATH% -DestinationPath %HEDEF_PATH%;}"
