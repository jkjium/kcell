#!/usr/bin/python

import sys
import os, time

from shutil import copyfile

from tinydb import TinyDB
import cell.common as cm
from cell import entry_cmd
from cell.entry import entmgr

import tests.test as tt

# init a cell directory
def init(arglist):
	if len(arglist)<3:
		print 'Initializ cell meta db.'
		print 'Usage: cell init cellname description\n'
		return

	if not os.path.exists(cm.entrydb):
		cellname = arglist[2]
		description = arglist[3]

		addcmd = ['','',cellname, description, 'tag=init']
		db = TinyDB(cm.entrydb) # create file
		em = entmgr(cm.entrydb)
		em.add(addcmd)
		print 'cell [%s] init done.' % cellname
	else:
		print 'cannot create cell meta: File (%s) exists' % cm.entrydb

	'''
	# check $PWD/.cellmeta 
	if not os.path.exists(cm.entrydb):
		# create db
		#db = TinyDB(cm.entrydb)
		em = entmgr(cm.entrydb)

		print 'cell [%s] init done.' % dbname
	else:
		print 'cannot create cell meta : File exists'
	'''

def rollback():
	copyfile(cm.entrydb()+'.shadow', cm.entrydb())

def help(d):
	print '--------------------'
	for name in d:
		d[name]([])
		print ''
	print '--------------------'

# main entrance
def main():
	dispatch = {
		'init' : init,
		'add'  : entry_cmd.add,
		'rm'   : entry_cmd.rm,
		'alter': entry_cmd.alter,
		'info' : entry_cmd.info,
		'rr'   : entry_cmd.alterrank,
		'ac'   : entry_cmd.altercontent,
		'dump' : entry_cmd.dump,
		#'test': tt.test,
		#'clean': tt.clean
	}

	if sys.argv[1] == 'init':
		init(sys.argv)
	elif sys.argv[1] == 'rollback':
		print 'restore rc db from last backup.'
		rollback()
	elif len(sys.argv)<2 or (sys.argv[1] not in dispatch):
		help(dispatch)
		print 'error::Invalid cmd string\n'
		exit(1)
	else:
		dispatch[sys.argv[1]](sys.argv)

if __name__ == '__main__':
	main()
