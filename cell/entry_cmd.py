import sys
import cell.common as cm

from tinydb import TinyDB, Query
from cell.entry import entry, entmgr


def altercontent(arglist):
	if len(arglist) < 4:
		print 'alter entry content by text reference number'
		print 'Usage: python cell.py ac rank target operation'
		print 'example'
		print 'python cell.py ac 10 3{+"insert newline",="replace line",-}'
		print '$ rc ac - ="kck"'
		return
	entmgr(cm.entrydb).altercontent(arglist)


def alterrank(arglist):
	if len(arglist) < 4:
		print 'change rank'
		print 'Usage: python cell.py rr oldrank newrank'
		print 'example: python cell.py rr 10 10.1'
		return
	entmgr(cm.entrydb).alterrank(arglist)


def alter(arglist):
	if len(arglist) < 4:
		print 'alter entry'
		print 'Usage: python cell.py alter rank {"query string" ...} "update value" ...'
		print 'example:'
		print 'python cell.py alter . stage:data'
		print 'python cell.py alter 2:5 stage=dvlp stage:dvlp-1'
		print 'python cell.py alter 2: tag=test stage=dvlp project:dvlp-1'
		return
	entmgr(cm.entrydb).alter(arglist)


def info(arglist):
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

	em = entmgr(cm.entrydb)
	sortlist = em.info(arglist)
	cm.fmtout(sortlist)

	print 'list %d records.' % len(sortlist)
	
def rm(arglist):
	"""
	rm entry(ies)
	"""
	if len(arglist) < 3:
		print 'rm entry(ies)'
		print 'Usage: python cell.py rm rank "query string" ...'
		print 'example: rc rm . tag=alter # remove all the entries tag contains alter'
		return
	entmgr(cm.entrydb).rm(arglist)


def add(arglist):
	"""
	Add an entry

	"""
	if len(arglist) < 4:
		print 'add en entry:'
		print 'Usage: python cell.py add ent.name content {tag=t1,t2,t3} {ext1=e1 ext2=e2}'
		print 'example: python cell.py add .pdb "protein structure file" tag=file,raw stage="data-collection" time="201705160615"'
		return
	entmgr(cm.entrydb).add(arglist)
	print 'entry added in %s' % cm.entrydb


def dump(arglist):
	print 'dump all records:\n---'
	entdb = TinyDB(cm.entrydb)
	cm.fmtout(entdb.all())

