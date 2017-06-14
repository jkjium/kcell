import sys
import os
import cell.core.common as cm

from tinydb import TinyDB, Query
from cell.core.entry import entry, entmgr

def register(arglist):
	em = entmgr(cm.cellroot)
	name = 'stage'
	content = os.getcwd()
	tag = 'tag=path'
	desc = 'desc=cell stage'
	if len(arglist) > 2:
		desc = 'desc='+arglist[2]
	addarg =['','',name,content,tag, desc] 
	em.add(addarg)
	print 'register current stage ok.'

def stagelist(arglist):
	args = ['','','.','name=stage']

	em = entmgr(cm.cellroot)
	sortlist = em.info(args)
	cm.fmtout(sortlist)

	print 'list %d records.' % len(sortlist)

def metarm(arglist):
	if len(arglist) < 3:
		print 'rm entry(ies)'
		print 'Usage: python cell.py rm rank "query string" ...'
		print 'example: rc rm . tag=alter # remove all the entries tag contains alter'
		return
	entmgr(cm.cellroot).rm(arglist)

def metaalter(arglist):
	if len(arglist) < 3:
		print 'rm entry(ies)'
		print 'Usage: python cell.py rm rank "query string" ...'
		print 'example: rc rm . tag=alter # remove all the entries tag contains alter'
		return
	entmgr(cm.cellroot).rm(arglist)	