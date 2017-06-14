import os
import time
from datetime import datetime
import common as cm
from tinydb import TinyDB, Query

__all__=['entry', 'entmgr']

# entry data structure
class entry(object):
	def __init__(self):
		self.name = '_DEFAULT' # short name for reference
		self.rank = 1001 # ordered reference number, unique
		self.content = '' # main content
		self.tag = ['_DEFAULT'] # tags for searching purpose
		self.property= {} # for any extend properties
		self.flag = -1 # for routine purpose, work in memory, never store in db

	def __str__(self):
		desc = self.content.split('\n')
		if 'ts' not in self.property:
			self.property['ts'] = '1497470916' #'2017-06-14 15:10:23'
		return '[%d] %s tag:[%s] {%s} %s\n>>\n%s' % (
				self.rank, 
				self.name, 
				','.join(set(self.tag)),
				','.join('%s:%s' % (p,self.property[p]) for p in self.property if p!='ts'),
				datetime.fromtimestamp(int(self.property['ts'])).strftime('%Y-%m-%d %H:%M:%S'),
				'\n'.join(('%d. %s' % (i, desc[i])) for i in range(len(desc)))
				)


# entry management
class entmgr(object):
	def __init__(self, dbname):
		if not os.path.exists(cm.cellhome):
			print 'cell db not exist. run "rc init" first.'
			exit(-1)
		self.db = TinyDB(dbname) 
		self.globalseq = cm.getmaxseq(self.db)


	def add(self, arglist):
		e = entry()
		e.name = arglist[2]
		e.content = arglist[3]
		self.globalseq+=1
		e.rank = self.globalseq 
		e.property['ts'] = int(time.time())

		# for optional properties
		if len(arglist) > 4:
			for arg in arglist[4:]:
				if 'tag' == arg[:3]:
					e.tag = arg[4:].split(',')
				else:
					e.property[arg[:arg.index('=')]] = arg[arg.index('=')+1:]

		# check for existance
		q = Query()
		ret = self.db.search(q.rank == e.rank) # return a list of dict
		if len(ret)>0:
			print 'error::rank conflict.' 
			print str(e)
			for r in ret:
				re = cm.loadent(r)
				print str(re)
		else:
			cm.saveent(self.db, e)
			print '\n---\n%s\n---\n' % str(e)
			print 'new entry added.'
			print self.globalseq		


	def info(self, arglist):
		'''
		input query string
		output sorted entry list

		'''
		elist = cm.parserank(self.db, arglist[2])
		retlist = elist
		if len(arglist)> 3:
			retlist = cm.filtercondition(elist, arglist[3:])

		return sorted(retlist, key=lambda e: float(e.rank))

	def rm(self, arglist):
		'''
		remove any entry that matches the conditions

		'''
		q = Query()
		elist = cm.parserank(self.db, arglist[2])
		retlist = elist
		if len(arglist)> 3:
			retlist = cm.filtercondition(elist, arglist[3:])	

		if len(retlist) >= len(self.db.all()):
			print 'Warning! All records will be purged. Use cell clean instead.'
			return

		cm.fmtout(retlist)
		for e in retlist:
			self.db.remove(q.rank == e.rank)
		print '%d record removed.' % len(retlist)		

	def altercontent(self, arglist):
		entdb = self.db
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


	def alterrank(self, arglist):

		entdb = self.db
		update = float(arglist[3])
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


	def alter(self, arglist):
		entdb = self.db
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


	def dump(self):
		print 'entmgr: %s' % self.db