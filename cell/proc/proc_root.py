import sys
import os
import cell.core.common as cm

from tinydb import TinyDB, Query
from cell.core.entry import entry, entmgr

def register(arglist):
	em = entmgr(cm.cellroot)
	name = 'cell stage'
	content = os.getcwd()
	tag = 'tag=path'
	desc = 'desc=cell stage'
	if len(arglist) > 2:
		desc = arglist[2]
	addarg =['','',name,content,tag, desc] 
	em.add(addarg)
	print 'register current stage ok.'

def stagelist(arglist):
	if len(arglist) < 3:
		print 'show entry info'
		print 'Usage: python cell.py info rank "query string" ...'
		print 'example:\npython cell.py info .'
		print 'python cell.py info . stage=dvlp'
		print 'python cell.py info 5:'
		print 'python cell.py info :5 tag=test,debug stage=dvlp'
		print 'python cell.py info 2:5 tag=debug stage=test'
		print 'python cell.py info -'
		return

	em = entmgr(cm.cellroot)
	sortlist = em.info(arglist)
	cm.fmtout(sortlist)

	print 'list %d records.' % len(sortlist)	