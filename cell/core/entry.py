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
		self.flag = -1# for routine purpose, work in memory, never store in db

	def __str__(self):
		desc = self.content.split('\n')
		return '[%d] [%s] [%s] [%s]\n>>\n%s' % (
				self.rank, 
				self.name, 
				','.join(set(self.tag)),
				','.join('%s:%s' % (p,self.property[p]) for p in self.property),
				'\n'.join(('%d. %s' % (i, desc[i])) for i in range(len(desc)))
				)


# entry management
class entmgr(object):
	def __init__(self, dbname):
		self.db = TinyDB(dbname) 
		self.globalseq = cm.getmaxseq(self.db)


	def add(self, arglist):
		e = entry()
		e.name = arglist[2]
		e.content = arglist[3]
		self.globalseq+=1
		e.rank = self.globalseq 

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



	def dump(self):
		print 'entmgr: %s' % self.db