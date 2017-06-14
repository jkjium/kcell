#!/usr/bin/python

import sys
import os
from shutil import copyfile

from tinydb import TinyDB
import cell.core.common as cm
from cell.proc import proc_entry, proc_root

import tests.test as tt

# init a cell directory
def init(arglist):
	if len(arglist)<2:
		print 'Initializ cell meta data.'
		print 'Usage: cell init\n'
		return
	if not os.path.exists(cm.cellhome):
		os.makedirs(cm.cellhome)
		db = TinyDB(cm.entrydb)
		# create db
		print 'cell init done.'
	else:
		print 'cannot create cell meta : File exists'
		#cellinfo()



def rollback():
	copyfile(cm.entrydb+'.shadow', cm.entrydb)

def help(d):
	print '--------------------'
	for name in d:
		d[name]([])
		print ''
	print '--------------------'

def _globalseq():
	cm.globalseq = cm.getmaxseq(TinyDB(cm.entrydb))
	#print 'global seq: %d' % cm.globalseq


# main entrance
def main():
	dispatch = {
		'init' : init,
		'add'  : proc_entry.add,
		'rm'   : proc_entry.rm,
		'alter': proc_entry.alter,
		'info' : proc_entry.info,
		'rr'   : proc_entry.alterrank,
		'ac'   : proc_entry.altercontent,
		'dump' : proc_entry.dump,
		#'test': tt.test,
		'register': proc_root.register,
		#'clean': tt.clean

		#'memo': proc_memo
	}
	if sys.argv[1] == 'init':
		init(sys.argv)
	elif sys.argv[1] == 'rollback':
		print 'restore db from last backup.'
		rollback()
	elif len(sys.argv)<2 or (sys.argv[1] not in dispatch):
		help(dispatch)
		print 'error::Invalid cmd string\n'
		exit(1)
	else:
		_globalseq()
		dispatch[sys.argv[1]](sys.argv)

if __name__ == '__main__':
	main()