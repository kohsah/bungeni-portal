#!/bin/bash
#===============================================================================
#
#          FILE:  svn_set_externals.sh
#
#         USAGE:  ./svn_set_externals.sh
#
#   DESCRIPTION:  Update subversion externals property
#
#       OPTIONS:  ---
#          BUGS:  ---
#         NOTES:  ---
#        AUTHOR:  Samuel Weru, samweru@gmail.com
#  ORGANIZATION:  UNDESA
#       VERSION:  ---
#       CREATED:  ---
#      REVISION:  ---
#===============================================================================
svn propset svn:externals -F externals.txt .