import sys
import os
from collections import defaultdict
from shutil import copyfile

from cell.core.entry import entry
from tinydb import TinyDB, Query

'''
wrapper module
'''
cellroot = os.path.expanduser('~') + '/.cellroot'
cellhome = '.cell'
entrydb = cellhome+'/entrydb'
draftdb = cellhome+'/draftdb'

globalseq = -1
assign = ':'
ext = '+'

ops = ['=','%'] # substring and regex
aps = [assign, ext] # assign and extend (for tag, content)

def backup():
        copyfile(entrydb, entrydb+'.shadow')

def lastentry(entdb):
	return sorted([loadent(re) for re in entdb.all()], key=lambda e: float(e.rank))[-1]
	
def updatename(elist, cond):
	(n,v,op) = parsecond(cond, aps) # use aps here
	if len(n) == 0:
		print 'invalid update statement %s' % cond
		exit(-1)
	for e in elist:
		e.name = v


def updatetag(elist, cond):
	(n,v,op) = parsecond(cond, aps)
	if len(n)==0:
		print 'invalid update statement: %s' % cond
		exit(-1)
	tags = v.split(',')
	print 'tags: %s' % repr(tags)
	for e in elist:
		if op == assign:
			e.tag = tags
		elif op == ext:
			e.tag+=tags # merge list into tag set


def updatecontent(elist, cond):
	(n,v,op) = parsecond(cond, aps)
	if len(n)==0:
		print 'invalid update statement: %s' % cond
		exit(-1)

	for e in elist:
		if op == assign:
			e.content = v
		elif op == ext:
			e.content += ('\n%s' % v) # start a new line


def updateproperty(elist, cond):
	(n,v,op) = parsecond(cond, aps)
	if len(n)==0:
		print 'invalid update statement: %s' % cond
		exit(-1)

	for e in elist:
		if op == assign:
			e.property[n] = v


def entryupdate(elist, condlist):
	condnum = len(condlist)
	print 'update num: %d' % condnum
	for c in condlist:
		if 'name' == c[:4]:
			updatename(elist, c)
		elif 'tag' == c[:3]:
			updatetag(elist, c)
		elif 'content' == c[:7]:
			updatecontent(elist, c)
		else:
			updateproperty(elist, c)
	return True

def filterarg(condlist):
	argcond= []
	argupdate = []
	for cond in condlist:
		if len([cond.index(a) for a in aps if a in cond])!=0:
			argupdate.append(cond)
		elif len([cond.index(a) for a in ops if a in cond])!=0:
			argcond.append(cond)

	return argcond, argupdate

def parsename(elist, cond):
	"""
	for name 
	"""
	(n,v,op) = parsecond(cond, ops)
	if len(n)==0:
		print 'invalid condition: %s' % cond
		exit(-1)

	for e in elist:
		if op == '=':
			if v in e.name:
				e.flag-=1


def parsecontent(elist, cond):
	(n,v,op) = parsecond(cond, ops)
	if len(n)==0:
		print 'invalid condition: %s' % cond
		exit(-1)

	for e in elist:
		if op == '=':
			if v in e.content:
				e.flag-=1


def parsetag(elist, cond):
	(n,v,op) = parsecond(cond, ops)
	if len(n)==0:
		print 'invalid condition: %s' % cond
		exit(-1)
	tags = v.split(',')
	for e in elist:
		if op == '=':
			if len([t for t in e.tag if t in tags])==len(tags):
				e.flag-=1	


def parsecond(cond, plist):
	"""
	parse properties condition such as [stage=data]
	"""
	ret = ('', '', '')
	oplist = [(c, cond.index(c)) for c in plist if c in cond]
	#print repr(oplist)
	if len(oplist)==1:
		op =oplist[0][0] 
		d = oplist[0][1]
		n = cond[:d]
		v = cond[d+1:]
		ret= (n,v,op)
	#print repr(ret)
	return ret

def parseproperty(elist, cond):
	"""
	for extend properties
	"""
	(n,v,op) = parsecond(cond, ops)
	if len(n)==0:
		print 'invalid condition: %s' % cond
		exit(-1)

	for e in elist:
		if n in e.property: # contain property
			if op == '=':
				if e.property[n] == v:
					e.flag-=1

			#elif op == ''
def filtercondition(elist, condlist):
	"""
	filter entry with all (&) conditions meet
	"""
	#print repr(condlist)
	#condnum = len([c for c in condlist if c in ('name','tag','content')]) + len(condlist)
	condnum = len(condlist)
	print 'cond num: %d' % condnum
	for e in elist:
		e.flag = condnum
	for c in condlist:
		if 'name' == c[:4]:
			parsename(elist, c)
		elif 'tag' == c[:3]:
			parsetag(elist, c)
		elif 'content' == c[:7]:
			parsecontent(elist, c)
		else:
			parseproperty(elist, c)

	return [e for e in elist if e.flag==0]


def parserank(entdb, rankstr):
	"""
	parse input string for rank query
	return (code, [list])
	"""
	if rankstr == '-':
		return [lastentry(entdb)]
	relist = []
	print 'rankstr: %s' % rankstr
	q = Query()
	if '.' == rankstr:
		relist = entdb.all()
	elif ':' in rankstr: # [:2]
		if ':' == rankstr[0]:
			relist = entdb.search( (q.rank >=0) & (q.rank <= float(rankstr[1:])) )
		elif ':' == rankstr[-1]: #[2:]
			relist = entdb.search((q.rank >= float(rankstr[:-1])) & (q.rank <= globalseq))
		else: #[2:5]
			rankr = [float(r) for r in rankstr.split(':')]
			relist = entdb.search( (q.rank>= rankr[0]) & (q.rank<=rankr[1]) )
	else:
		for r in rankstr.split(','):
			relist+=entdb.search(q.rank == float(r))

	#print repr(relist)	
	return [loadent(re) for re in relist]


def loadent(dbent):
	e = entry()
	for k in dbent:
		if k == 'name':
			e.name = dbent['name']
		elif k == 'rank':
			e.rank = dbent['rank']
		elif k == 'content':
			e.content = dbent['content']
		elif k == 'tag':
			e.tag = dbent['tag'].split(',')
		else:
 			e.property[k] = dbent[k]
	return e


def saveent(entdb, e):
	#backup()
	tagstr = ','.join(set(e.tag))
	keyword = {'name':e.name, 'rank':e.rank, 'content':e.content, 'tag':tagstr}
	objdict = e.property.copy()
	objdict.update(keyword) # combine two dictionary
	entdb.remove(Query().rank == e.rank) # make sure there is no duplication
	entdb.insert(objdict)

def getmaxseq(entdb):
	ranklist = [loadent(re).rank for re in entdb.all()]
	if len(ranklist) == 0:
		return 0
	else:
		return int(max(ranklist))


def fmtout(elist):
	print 'output records:\n---'
	for e in elist:
		print '\n%s\n' % str(e)
	print '---'