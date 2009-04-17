#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# PyBorg: The python AI bot.
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
import re

def _load_config(filename):
	"""
	Load a config file returning dictionary of variables.
	"""
	import logging
	logger = logging.getLogger('logger')
	logger.debug('in _load_config')
	OK=True
	params=None

	re1=re.compile(r'^[^=]+=[^=]+$')  # format of config line: param = value
	
	try:
		f = None
		f = open(filename, "r")
		params = {}
		count = 0
		cont = False     # continuation line?
		buf=''
		
		while True:
			line = f.readline() 
			if not line: break
			count = count + 1
			line=line.strip()
			if line=="" or line[0]=='#': continue
			if cont:
				# previous line was continued
				buf = '%s%s' % (buf, line)
			else:
				buf=line
			
			if line[-1] == '\\':
				# current line is continued with backslash
				cont = True
				buf=buf[:-1]
			else:
				if line[-1] == ',':
					# current line ends with ',', so is continued
					cont = True
				else:
					if not re1.match(buf):
						logger.error("Malformed line in %s line %d: %s" % (filename, count, buf))
					else:	
						head, sep, tail = buf.partition('=')
						logger.debug('head = %s; tail = %s' % (head, tail))
						try:
							params[head.strip()]=eval(tail.strip())
						except:
							logger.error("Malformed line in %s line %d: %s" % (filename, count, buf))
						else:
							buf=''

	except IOError, e:
		# config file does not exist when building a new dictionary
		logger.info('IOerror', exc_info=True) 
		if find(e, 'No such file') > -1:
			logger.info('%s does not exist, creating it now..' % filename)
			OK=True
		else:
			OK=False
			raise
	except:
		logger.error('Unexpected exception raised:', exc_info=True) 
		OK=False
		raise
	finally:
		logger.debug('close config file and return result')
		if f: f.close()
		if OK:
			return params
		else:
			return None

		
def _save_config(filename, fields):
	"""
	fields should be a dictionary. Keys as names of
	variables containing tuple (string comment, value).
	Returns True if save OK; else returns False
	"""
	import logging
	logger = logging.getLogger('logger')
	logger.debug('in _save_config')
	result=False

	try:
		f = None
		f = open(filename, "w")

		# write the values with comments. this is a silly comment
		for key in fields.keys():
			logger.debug('key = %s; value = %s' % (key, fields[key][1]))
			# f.write("# "+fields[key][0]+" #\n")
			f.write("# %s #\n" % fields[key][0])
			s = repr(fields[key][1])
			# f.write(key+"\t= ")
			f.write("%s\t= " % key)

			#Create a new line after each dic entry
			if s.find("],") != -1:
				cut_string = ""
				while s.find("],") != -1:
					position = s.find("],")+3
					cut_string = cut_string + s[:position] + "\n\t"
					s = s[position:]
				s = cut_string + s
				f.write('%s\n' % s)
				continue

		        #If the line exceeds a normal display ( 80 col ) cut it
			width=60
			if len(s) > width:
				cut_string = ""
				while len(s) > width:
					position = s.rfind(",",0,width)+1
					cut_string = '%s%s\n\t\t' % (cut_string, s[:position])
					s = s[position:]
				s = '%s%s' % (cut_string, s)
			f.write("%s\n" % s)
		result=True

	#f.write("# End of configuration #")
	except IOError, e:
		logger.error('IOError', exc_info=True) 
	except:
		logger.error('Unexpected exception caught.', exc_info=True) 
	finally:
		logger.debug('close config file and return result')
		if f: f.close()
		return result


class BorgConfig:
	def __init__(self):
		import logging
		self.logger = logging.getLogger('logger')
		
	def load(self, filename, kwargs=None):
		"""
		Defaults should be key=variable name, value=
		tuple of (comment, default value)
		"""
		self.logger.debug('in BorgConfig.load()')
	
		# default config params
		defaults = {
			"num_contexts": ("Total word contexts", 0),
			"num_words":	("Total unique words known", 0),
			"max_words":	("Maximum words known", 6000),
			"learning":	("Learning on", 1),
			"ignore_list":  ("Words that can be ignored", ['!', '?', "'", ',', ';', '.']),
			"censored":	("Don't learn the sentence if it contains one of these words", []),
			"num_aliases":  ("Total aliases known", 0),
			"aliases":	("List of aliases", {}),
			"process_with": ("Generate a reply with (mcborg|megahal)", "mcborg"),
			"no_save":      ("Dont save the dictionary and configuration to disk", "False")
			}
		if not kwargs: kwargs = defaults
		self._defaults = kwargs
		self._filename = filename

		for i in defaults.keys():
			self.__dict__[i] = defaults[i][1]

		# try to load saved config
		params = _load_config(filename)
		if params == None:
			# none found. building new dictionary?
			self.logger.debug('params = %s' % params)
			self.save()
			return
		for i in params.keys():
			self.__dict__[i] = params[i]
		self.logger.debug('params = %s' % params)

	def save(self):
		"""
		Save borg settings
		"""
		self.logger.debug('in BorgConfig.save()')
		
		keys = {}
		# attributes exempt from saving in config file
		exempt=('_defaults', '_filename', 'logger')
		for i in self.__dict__.keys():
			if i in exempt:
				continue
			comment, value = self._defaults.get(i, ('', None))
			keys[i] = (comment, self.__dict__[i])
		# save to config file
		return _save_config(self._filename, keys)

if __name__ == '__main__':
	import sys
	import logging
	logger = logging.getLogger('logger')
	handler = logging.FileHandler('trace.log')
	format = logging.Formatter('%(asctime)s %(module)s %(lineno)d %(levelname)s %(message)s')
	handler.setFormatter(format)
	handler.setLevel(logging.DEBUG)
	logger.addHandler(handler)
	logger.setLevel(logging.DEBUG)

	logger.debug('#------- start program %s ----------#' % sys.argv[0])
	config=BorgConfig()
	config.load('mcborg.cfg', None)
	logger.debug('config.ignore_list = %s' % config.ignore_list)
	if config.save():
		logger.debug('Config saved OK.')
	else:
		logger.error('Could not save config file.')
