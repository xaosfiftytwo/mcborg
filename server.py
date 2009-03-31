#!/usr/bin/env python
#
# Mcborg Telnet module (fairly raw 'telnet'...)
# Defaults to listening on port 8489
#
# Copyright (c) 2000, 2001 Tom Morton
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
import sys
import string
import socket
import SocketServer

import mcborg

class handler(SocketServer.BaseRequestHandler):
	# Command list for this module
	commandlist = "Telnet Module Commands:\n!quit"
	commanddict = {}
	
	def handle(self):
		####
		if ("-v" in sys.argv) or ("--verbose" in sys.argv):
			self.opt_verbose = 1
		else:
			self.opt_verbose = 0
		####
		print "Connection from ", self.request.getpeername()
		self.request.send("\r\nMcborg. Type !quit to leave.\r\n")
		while 1:
			try:
				self.request.send("> ")
				body = ""
				while 1:
					new = self.request.recv(1000)
					if new[-2:] != "\r\n":
						if new == '\x08':
							body = body[:-1]
						else:
							body = body + new
					else:
						body = body + new
						break
			except socket.error, e:
				print "Closed connection to", self.request.getpeername(), ": ", e, e.args
				return
			else:
				if self.opt_verbose:
					print "%s --> \"%s\"" % (self.request.getpeername(), body[:-2])
				# Telnet module commands.
				if string.lower(body[0:5]) == "!quit":
					self.output("Bye", None)
					print "Closed connection to", self.request.getpeername(), ". User quit."
					return
				else:
					my_mcborg.process_msg(self, body, 100, 1, None, owner=0)

	def output(self, message, args):
		"""
		Output mcborg reply.
		"""
		if self.opt_verbose:
			print "%s <-- \"%s\"" % (self.request.getpeername(), message)
		try:
			self.request.send(message+"\r\n")
		except:
			pass	

if __name__ == '__main__':
# handle command line options

	def usage():
		print "Mcborg telnet module."
		print
		print "-v --verbose"
		print "-p --port n      Listen on port n (Defaults to 8489)"
		print
		sys.exit(0)

	port = 8489
 
	try:
		opts, args = getopt.getopt(sys.argv[1:], "hp", ["help", "port"])
	except getopt.GetoptError, err:
		# print help information and exit:
		print str(err) # will print something like "option -a not recognized"
		usage()
		sys.exit(2)
	testing = False
	for o, a in opts:
		if o in ("-h", "--help"):
			usage()
			sys.exit()
		else:
			if o in ("-p", "--port"):
				try:
					port = int(a)
				except ValueError, e:
					print "Port number is not a valid number."
					sys.exit(2)
			else:
				assert False, "unhandled option"
	# start the damn server
	try:
		# server = SocketServer.ThreadingTCPServer(("", port), handler)
		server = SocketServer.ThreadingTCPServer(("localhost", port), handler)
	except socket.error, e:
		print "Socket error: ", e.args
	else:
		print "Starting mcborg..."
		my_mcborg = mcborg.mcborg()
		print "Awaiting connections on port %d ..." % port
		try:
			server.serve_forever()
		except KeyboardInterrupt, e:
			print "Server shut down"
		my_mcborg.save_all()
		del my_mcborg

