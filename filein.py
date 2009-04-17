#!/usr/bin/env python
#
# Mcborg ascii file input module
#
# Copyright (c) 2000, 2006 Tom Morton, Sebastien Dailly
#
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#        
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.
#
import string
import sys

import mcborg

class FileInput:
	"""
	Module for file input. Learning from ASCII text files.
	Takes its input from sys.stdin.
	"""

	# Command list for this module
	commandlist = "FileIn Module Commands:\nNone"
	commanddict = {}
	
	def __init__(self, borg, args):

		import logging
		self.logger = logging.getLogger('logger')
		
		buf = sys.stdin.read()

 		self.logger.info("I knew %s words (%d lines) before." % (borg.settings.num_words, len(borg.lines)))
		buf = mcborg.filter_message(buf, borg)
		# Learn from input
		try:
			borg.learn(buf)
		except KeyboardInterrupt, e:
			# Close database cleanly
			self.logger.error("Premature termination :-(", exc_info=True)
 		self.logger.info("I know %s words (%d lines) now." % (borg.settings.num_words, len(borg.lines)))

	def shutdown(self):
		pass

	def start(self):
		sys.exit()

	def output(self, message, args):
		pass

if __name__ == "__main__":
	import logging
	logger = logging.getLogger('logger')
	handler = logging.FileHandler('trace.log')
	format = logging.Formatter('%(asctime)s %(module)s %(lineno)d %(levelname)s %(message)s')
	handler.setFormatter(format)
	handler.setLevel(logging.DEBUG)
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)

	logger.debug('#------- start program %s ----------#' % sys.argv[0])
	myborg = mcborg.McBorg()
	FileInput(myborg, sys.argv)
	myborg.save_all()
	del myborg

