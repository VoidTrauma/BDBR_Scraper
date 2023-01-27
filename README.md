# BDBR_Scraper

1) Download repo
  (for those less familiar with github, click "code" and download the zip.)

2) open terminal at repo directory
  (mac users: right click the downloaded and unzipped directory, hover over the "services" option in the context menu and select "New Terminal At Folder"
  Windows users: hold down the Shift key and right-click on the desktop. In the context menu, you will see the option to "Open Poweshell Window" here. Click that. Older versions of Windows 10 will instead have the option to "Open command window here" and should click that. Note: Windows user may have to install python it is not already, see: https://www.python.org/downloads/windows/)

3) install requirements by running: pip install -r requirements.txt

4) run: python cdcr_scraper_v4.py

5) dismantle the carceral state

If you get permissions errors, run: chown -R $USER:$USER /path/to/directory

$USER is a global environment variable that refers to the current logged in user.

/path/to/directory should be replaced with the path to where you want to write to.
