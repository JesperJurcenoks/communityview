#!/usr/bin/python

################################################################################
#
# Copyright (C) 2012-2014 Neighborhood Guard, Inc.  All rights reserved.
# Original author: Jesper Jercenoks
# 
# This file is part of CommunityView.
# 
# CommunityView is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# CommunityView is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
# 
# This script was adapted from http://code.activestate.com/recipes/273844-minimal-http-upload-cgi/
# with updates from http://stackoverflow.com/questions/12166158/upload-a-file-with-python 
#
# This script has security risks. A user could attempt to fill
# a disk partition with endless uploads.
# If you have a system open to the public you would obviously want
# to limit the size and number of files written to the disk.
#
# You should have received a copy of the GNU Affero General Public License
# along with CommunityView.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################

################################################################################
#                                                                              #
# Version String                                                               #
#                                                                              #
################################################################################

version_string = "0.9.0"

import cgi
import cgitb; cgitb.enable()
import os, sys
import shutil
import re
import localsettings
import communityview
import logging

HTML_TEMPLATE = """
<html><head><title>File Upload</title>
<meta http-equiv="Content-Type" content="text/html; charset=iso-8859-1">
</head>
<body><h1>File Upload</h1>
Filename: %s<br>
%s<br>
<form action="" method="POST" enctype="multipart/form-data">
Date [yyyy-mm-dd] : <input type="text" name="date">
Camera short name [a-z_0-9-]: <input type="text" name="camera">
File name hh-mm-ss-nnnnnnn.jpg: <input name="file" type="file"><br>
<input type="checkbox" value="true" name="status"> Status file<br>
<input name="submit" type="submit">
</form>
</body>
</html>"""

def print_html_form (error, outpath):
    """This prints out the html form. Note that the action is set to
      the name of the script which makes this is a self-posting form.
      In other words, this cgi both displays a form and processes it.
    """
    print "content-type: text/html\n"
    print HTML_TEMPLATE % (outpath, error)

    return
    
def save_uploaded_file ():
    error = ""
    outpath = ""
    """This saves a file uploaded by an HTML form.
       The form_field is the name of the file input field from the form.
       For example, the following form_field would be "file_1":
           <input name="file_1" type="file">
       The upload_dir is the directory where the file will be written.
       If no file was uploaded or if the field does not exist then
       this does nothing.
    """
    
    
    form = cgi.FieldStorage()

    if form.has_key("submit"):
        if not form.has_key("file"):
            error = "Error: form has no input 'file'"
        else :
            fileitem = form["file"]
            if not fileitem.file or not fileitem.filename: 
                error = "Error: file form fields is not type=file"
            else:
                logging.info("filename = '%s'" % fileitem.filename)
                if not form.has_key("camera"):
                    error = "no camera submitted"
                else:
                    camerashortname_raw = form["camera"].value
                    if camerashortname_raw <> None:
                        matchobject=re.match("[\w-]*", camerashortname_raw)
                        if matchobject==None or matchobject.group(0) == "" or len(camerashortname_raw) <> len(matchobject.group(0)):
                            error = "Invalid Camera name"
                        else:
                            camerashortname = matchobject.group(0)
                            logging.info("camerashortname = '%s'" % camerashortname)
                            if form.has_key("status") and form["status"].value == "true" :
                                logging.info("status = true")
                                # deliberately breaking this into two parts each using a single mkdir instead of using the recursive mkdirs. This is a security measure, preventing uncontrolled directory creation it something passes the filter
                                statusdir=os.path.join(localsettings.root, "status")
                                communityview.mkdir(statusdir)
                                cameradir=os.path.join(statusdir, camerashortname) 
                                communityview.mkdir(cameradir)
                                outpath = os.path.join(cameradir, fileitem.filename)
                                with open(outpath, 'wb') as fout:
                                    try:
                                        shutil.copyfileobj(fileitem.file, fout, 100000)
                                    except:
                                        error = "unknown error writing file to disk"
                            else:

                                date_raw = form["date"].value
                                if date_raw <> None:
                                    matchobject=re.match("[\d-]*", date_raw)
                                    if matchobject==None or matchobject.group(0) == "" or len(date_raw) <> len(matchobject.group(0)):
                                        error = "Invalid date"
                                    else:                                                              
                                        image_date = matchobject.group(0)
                                        logging.info("date = '%s'" % image_date)
                                        # deliberately breaking this into two parts each using a single mkdir instead of using the recursive mkdirs. This is a security measure, preventing uncontrolled directory creation it something passes the filter
                                        datedir = os.path.join(localsettings.root, image_date) 
                                        communityview.mkdir(datedir)
                                        cameradir = os.path.join(datedir, camerashortname) 
                                        communityview.mkdir(cameradir)
                                        outpath = os.path.join(cameradir, fileitem.filename)
                                        
                                        with open(outpath, 'wb') as fout:
                                            try:
                                                shutil.copyfileobj(fileitem.file, fout, 100000)
                                            except:
                                                error = "unknown error writing file to disk"

    if error <> "" :
        logging.error(error)
    logging.info("outpath = '%s'" % outpath)
    return (error, outpath)


def main():    
    communityview.set_up_logging('communityview_upload_image.log')
    logging.info("Program Started, version %s", version_string)

    (error, outpath) = save_uploaded_file ()

    print_html_form (error, outpath)


if __name__ == "__main__":
    main()
