import sys
import cell.core.common as cm

from tinydb import TinyDB, Query
from cell.core.entry import entry, entmgr


def altercontent(arglist):
	if len(arglist) < 4:
		print 'alter entry content by text reference number'
		print 'Usage: python cell.py ac rank target operation'
		print 'example'
		print 'python cell.py ac 10 3{+"insert newline",="replace line",-}'
		print '$ rc ac - ="kck"'
		return


	entdb = TinyDB(cm.entrydb)
	if arglist[2] == '-':
		e = cm.lastentry(entdb)
	else:
		rank = float(arglist[2])
		e = cm.loadent(entdb.search(Query().rank == rank)[0])
	print '--- original record ---'
	print '\n%s' % str(e)

	clist = e.content.split('\n')
	cond = arglist[3]
	i = [c.isdigit() for c in cond].index(False) # find the first occurance of non digit character
	if i == 0:
		textid = len(clist)	- 1
	else:
		textid = int(cond[:i])

	update = cond[i:]
	if textid > (len(clist)-1):
		print 'error::invalid text id %d' % textid
		return
	op = update[0]
	if op == '+':
		v = update[1:]
		clist[textid] = '%s\n%s' % (clist[textid], v)
	elif op == '=':
		v = update[1:]
		clist[textid] = v
	elif op == '-':
		del clist[textid]
	else:
		print 'error::invalid operation %s' % op
		return

	e.content = '\n'.join(clist)
	print '--- updated record ---'
	print '\n%s\n' % str(e)
	cm.saveent(entdb, e)


def alterrank(arglist):
	if len(arglist) < 4:
		print 'change rank'
		print 'Usage: python cell.py rr oldrank newrank'
		print 'example: python cell.py rr 10 10.1'
		return

	update = float(arglist[3])

	entdb = TinyDB(cm.entrydb)
	elist = [cm.loadent(re) for re in entdb.all()]
	ranklist = [e.rank for e in elist]
	if update in ranklist:
		print 'error::new rank exist!'
		return
	if arglist[2] == '-':
		target = max(ranklist)
	else:
		target = float(arglist[2])
		if target not in ranklist:
			print 'error::old rank not exist!'
			return

	entdb.remove(Query().rank == target)
	for e in elist:
		if e.rank == target:
			print '--- original record ---'
			print '\n%s' % str(e)				
			e.rank = update
			print '\n%s\n' % str(e)
			cm.saveent(entdb, e)
			return


def alter(arglist):
	if len(arglist) < 4:
		print 'alter entry'
		print 'Usage: python cell.py alter rank {"query string" ...} "update value" ...'
		print 'example:'
		print 'python cell.py alter . stage:data'
		print 'python cell.py alter 2:5 stage=dvlp stage:dvlp-1'
		print 'python cell.py alter 2: tag=test stage=dvlp project:dvlp-1'
		return

	entdb = TinyDB(cm.entrydb)
	elist = cm.parserank(entdb, arglist[2])
	retlist = elist
	argcond, argupdate = cm.filterarg(arglist[3:])
	#print 'argcond: %s' % repr(argcond)
	#print 'argupdate: %s' % repr(argupdate)

	retlist = cm.filtercondition(elist, argcond)
	print '--- original records ---'
	cm.fmtout(retlist)

	ret = cm.entryupdate(retlist, argupdate)
	print '--- updated records ---'
	cm.fmtout(retlist)

	for e in retlist:
		cm.saveent(entdb, e)

	print 'update %d records.' % len(retlist)


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
		print 'example:'
		return

	entdb = TinyDB(cm.entrydb)
	q = Query()
	elist = cm.parserank(entdb, arglist[2])
	retlist = elist
	if len(arglist)> 3:
		retlist = cm.filtercondition(elist, arglist[3:])	

	if len(retlist) >= len(entdb.all()):
		print 'Warning! All records will be purged. Use cell clean instead.'
		return

	cm.fmtout(retlist)
	for e in retlist:
		entdb.remove(q.rank == e.rank)
	print '%d record removed.' % len(retlist)


def add(arglist):
	"""
	Add an entry

	"""
	if len(arglist) < 4:
		print 'add en entry:'
		print 'Usage: python cell.py add ent.name content {tag=t1,t2,t3} {ext1=e1 ext2=e2}'
		print 'example: python cell.py add .pdb "protein structure file" tag=file,raw stage="data-collection" time="201705160615"'
		return
	em = entmgr(cm.entrydb)
	em.add(arglist)
	print 'entry added in %s' % cm.entrydb


def dump(arglist):
	print 'dump all records:\n---'
	entdb = TinyDB(cm.entrydb)
	cm.fmtout(entdb.all())

