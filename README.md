# PDFdownload

## Requirements
Selenium 3.4.1
Python 3.6.1
Windows 10
Chrome webdriver
data.txt file specifying required program inputs
## Description
`PDFdownload.py` navigates to a course home page and logs the user in with provided credentials using a Chrome driver and Selenium 3.4.1 package. The python script then navigates to a specified course page and downloads all class materials into a download folder on the hard drive. The script then organizes the downloaded files by file type in the download folder.

## Usage
`$> python _path_to_PDFdownload.py -d _path_to_data.txt -b _desired_browser`
Example:
`$> python ~/PDFdownload/PDFdownload.py -d ~/PDFdownload/data.txt -b chrome`

## Improvements
Many values for HTML codes are hardcoded into the script. All hardcoded dependencies are documented in potential_hardcodes.txt
## User input
### data.txt
#### Description
data.txt file specifies all required user inputs
#### Format
username {your_username}
password {your_password}
course {your course number}
term {your term number}
#### Example
username john_doe
password foo123
course ME327-03
term 1920W
### Global constants
MOODLE_URL : specifies the link to Rose-Hulman moodle sign-in screen
DOWNLOAD_DIR : specifies absolute path to desired download directory
ZIP_EXT : file extension of default system .zip files
## Notes to reader
1. `PDFdownload.py` was written for a Rose-Hulman student. It is deeply dependent on the school course management system, hosted on https://moodle.rose-hulman.edu. Edits should be made so that HTML tags and files are found properly for other websites, but this functionality is not currently supported. Things that are affected by the moodle dependency:

   a. Course numbers and term numbers (ex. 1920W ME327-03)

   b. Login screen

   c.  Course pages

   d. Location of course content

   e. Format of course links and resources

2. It is assumed the user can follow proper installation of a Python 3 environment with successful installation/build of Selenium 3.4.1.
3. It is assumed the user can find a Chrome (or other web browser) driver and store it in a `./drivers` directory, relative to the location of the `PDFdownload.py` script.
4. If another web driver besides Chrome is desired, the user is responsbile for setting up preferences. These preferences should ensure that pdf/other files download immediately upon being clicked from a web page, rather than opening a new tab, such as `Chrome PDF viewer`. These things tend to mess up the whole script.
5. The `PDFexec.bat` batch file is just a convenient way to start the python script on windows. This should be edited to match your system files.
6. All development for this script was performed in a Visual Studio environment for Python.

   