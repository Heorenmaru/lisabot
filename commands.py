##LisaBot - IRC Bot
##Copyright (C) 2012 DeltaQuad
##This program is free software: you can redistribute it and/or modify
##it under the terms of the GNU General Public License as published by
##the Free Software Foundation, either version 3 of the License, or
##(at your option) any later version.
##This program is distributed in the hope that it will be useful,
##but WITHOUT ANY WARRANTY; without even the implied warranty of
##MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##GNU General Public License for more details.
##You should have received a copy of the GNU General Public License
##along with this program.  If not, see <http://www.gnu.org/licenses/>.

# -*- coding: utf-8  -*-

## Import basics.
import sys, socket, string, time, codecs, os, traceback, thread, re, urllib, web, math, unicodedata

## Import our functions.
import config, time

## Set up constants.
HOST, PORT, NICK, IDENT, REALNAME, CHANS, REPORT_CHAN, WELCOME_CHAN, META_CHAN, HOST2, PORT2, CHAN2, BOT, OWNER, PASS = config.host, config.port, config.nick, config.ident, config.realname, config.chans, config.report_chan, config.welcome_chan, config.meta_chan, config.host2, config.port2, config.chan2, config.bot, config.owner, config.password

KEY=config.key

## MySQL constants for access commands
op=2
voice=3
ban=4
kick=5
globalmsg=6
startup=7
quiet=8
nick=9
mode=10
trout=11
permission=12
restart=13
joinpart=14
blocked=15

def authdb(host, chan):
        import MySQLdb, traceback
        db = MySQLdb.connect(db="u_deltaquad_rights", host="sql", read_default_file="/home/deltaquad/.my.cnf")
        specify = host

        #new group system
        db.query("SELECT * FROM groups;")
        r = db.use_result()
        entry = r.fetch_row(maxrows=0)
        for group in entry:
                if group[0] in chan.lower():chan = group[1]
        time.sleep(.5)
        ####Temp disable to try new group system
        #if "techessentials" in chan.lower():chan = "@te"
        #if "deltaquad" in chan.lower() or "lisabot" in chan.lower():chan = "@dq"
        #if "openglobe" in chan.lower() or "lisabot" in chan.lower():chan = "@openglobe"
                
        if " " in specify: specify = string.split(specify, " ")[0]
        if not specify or "\"" in specify:
                reply("Please include the name of the entry you would like to read after the command, e.g. !notes read earwig", chan, nick)
                print "error"
        if '@' not in specify:specify = '@' + specify
        try:
                db.query("SELECT * FROM accessnew WHERE cloak = \"%s\" AND channel = \"%s\";" %(specify,chan))
                r = db.use_result()
                try:
                        data = r.fetch_row(0)[0]
                        print data[5]
                        auth = data
                except:auth = ['@none', '@global', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                db.query("SELECT * FROM accessnew WHERE cloak = \"%s\" AND channel = \"@global\";" %specify)
                rglobal = db.use_result()
                try:
                        authglobal = rglobal.fetch_row(0)[0]
                        print authglobal[5]
                except:authglobal = ['@none', '@global', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
                count = 0
                authfinal = []
                authfinal.insert(-1, '@%s'%host)
                authfinal.insert(1, chan)
                for entry in authglobal:
                        count = count + 1
                        try:float(entry)
                        except ValueError:continue
                        if entry == 0:authfinal.insert(count-1, auth[count-1]) 
                        else:
                                try:
                                        authfinal[count-1] = authglobal[count-1]
                                except:
                                        authfinal.insert(count-1, authglobal[count-1]) 
                #print authfinal
                return authfinal
        except:
                trace = traceback.format_exc() # Traceback.
                print trace # Print.
                return

def authtest(host, chan):
        if not "@" in host:host= "@" + host
        print "AuthDB"
        try:return authdb(host, chan)
	except:return False
def get_commandList():
	return {
	'join': 'join',
	'part': 'part',
		'leave': 'part',
	'restart': 'restart',
	'quit': 'quit',
		'die': 'quit',
		'suicide': 'quit',
	'langcode': 'langcode',
		'lang': 'langcode',
	'number': 'number',
		'count': 'number',
		'num': 'number',
	'nick': 'nick',
	'promote': 'promote',
	'demote': 'demote',
	'voice': 'voice',
	'devoice': 'devoice',
	'trout': 'trout',
		'fish': 'trout',
    'request': 'request',
    	'page': 'request',
	'kill': 'kill',
		'destroy': 'kill',
		'murder': 'kill',
	'commands': 'commands',
	'help': 'help',
		'doc': 'help',
		'documentation': 'help',
	'reminder': 'reminder',
		'remind': 'reminder',
    'ban': 'ban',
    'kick': 'kick',
    'unban': 'unban',
    'kickban': 'kickban',
    'quiet': 'quiet',
    'unquiet': 'unquiet',
    'sayhi': 'sayhi',
    'globalmsg': 'globalmsg',
    'stalk': 'stalk',
    'unstalk': 'unstalk',
    'hide': 'hide',
    'unhide': 'unhide',
    'blockinfo': 'blockinfo',
    'ipinfo': 'ipinfo',
    'pull': 'pull',
    'chan': 'chan',
    'myhost', 'myhost',
    'git': 'git',
    	'github': 'git',
    'msg': 'msg',
    'me': 'me',
    'mode': 'mode',
    'startup': 'startup',
    'geolocate': 'geolocate',
    	'geo': 'geolocate',
    'sql': 'sql',
    	'perms': 'sql'
	}

def main(command, line, line2, nick, chan, host, auth, notice, say, reply, s, s2, lastlink):
	try:
		parse(command, line, line2, nick, chan, host, auth, notice, say, reply, s, s2, lastlink)
	except Exception:
		trace = traceback.format_exc() # Traceback.
		print trace # Print.
		lines = list(reversed(trace.splitlines())) # Convert lines to process traceback....
		report2 = [lines[0].strip()]
		for line in lines: 
			line = line.strip()
			if line.startswith('File "/'): 
				report2.append(line[0].lower() + line[1:])
				break
		else: report2.append('source unknown')
		say(report2[0] + ' (' + report2[1] + ')', chan)

def parse(command, line, line2, nick, chan, host, auth, notice, say, reply, s, s2, lastlink):
	actionlevel = authtest(host, chan)
	print actionlevel
	try:
                if actionlevel[blocked] == 1:return
        except:
                import traceback
                trace = traceback.format_exc() # Traceback.
		print trace # Print.
                say("Error with obtaining your access codes.", chan)
                return
        if command == "blockinfo":
                say(blockinfo(" ".join(line2[4:])), chan)
                return
        if command == "ipinfo":
                say(blockinfo(line2[4]), chan)
                say(getGeo(line2[4]),chan)
                return
        if command == "pull":
                if actionlevel[restart] == 1:
                        try:
                                import sys
                                sys.path.append("/home/deltaquad/")
                                os.system("git pull git@github.com:dqwiki/lisabot")
                                reply("Done.", chan, nick)
                        except:
                                reply("Error.", chan, nick)
                else:
                        reply("Access denied, you need the +r (restart) to use this action.", chan, nick)
                return
	if command == "restart":
		import thread, time
		if actionlevel[restart] == 1:
                        s.send("QUIT\r\n")
                        s.shutdown(socket.SHUT_RDWR)
                        time.sleep(2)
                        s2.send("QUIT\r\n")
                        s2.shutdown(socket.SHUT_RDWR)
			time.sleep(2)
			#os.system("exit")
			os.system("clear")
			os.system("nice -15 python main.py")
			os.abort()
			sys.exit("Trying to end process.")
			raise KeyboardInterrupt
		else:
			reply("Access denied, you need the +r (restart) flag to use this action.", chan, nick)
		return
	if command == "chan":
                reply(chan, chan, nick)
        if command == "request":
                if actionlevel[trout]==0:
                        reply("Access denied, you need the +t (trout) flag to use this action.", chan, nick)
                        return
                #say(line2[4] + " to " + line2[5] +". Thank You!", chan)
                notice(nick, "Thank you for using the LisaBot paging system. Your message has been delievered over PM.")
                try:
                        notice(line2[4], "You have been requested to: " + line2[5] + " by " + nick + " for " + ' '.join(line2[6:]))
                except:
                        try:
                                notice(line2[4], "You have been requested by " + nick)
                        except:
                                notice(nick, "Your request format is invalid.")
                return
	if command == "myhost":
                reply(host, chan, nick)
                return
	if command == "sayhi":
                lisabot = "*waves* Hello, I am LisaBot. I run off of the Willow server on the Wikimedia Toolserver."
                reply(lisabot, chan, nick)
                return
	if command == "help":
                reply("Dsiabled.", chan, nick)
                return
        if command == "git":
                reply("https://github.com/dqwiki/lisabot/", chan, nick)
                return
	if command == "globalmsg":
		if actionlevel[globalmsg] == 1:
			msg = "Global Notice for LisaBot: "		
                        msg = msg + ' '.join(line2[4:])
			notice("#wikipedia-en-abuse", msg)
			notice("#wikipedia-en-spi", msg)
			notice("##DeltaQuad", msg)
			notice("##LisaBot", msg)
			notice("##DeltaQuad-private", msg)
			notice("#techessentials", msg)
			notice("#techessentials-staff", msg)
			notice("#techessentials-security", msg)
		else:
			reply("Access denied, you need the +g (global) global to use this action.", chan, nick)
		return
	if command == "join":
		if actionlevel[joinpart] == 1:
			try:
				channel = line2[4]
			except Exception:
				channel = chan
			s.send("JOIN %s\r\n" % channel)
			reply('Done!', chan, nick)
		else:
			reply("Access denied, you need the +j (join/part) flag to use this action.", chan, nick)
		return
	if command == "part":
		if actionlevel[joinpart] == 1:
			try:
				channel = line2[4]
			except Exception:
				channel = chan
			if not '#' in channel:
                                reason = channel
                                channel = chan
                        try:
                                reason = line2[5] + " (Requested by " +nick+")"
                                reply('Bye Bye!', chan, nick)
                                s.send("PART %s\r\n" % (channel,reason))
                        except:
                                reason = "Requested by " +nick+")"
                                reply('Bye Bye!', chan, nick)
                                s.send("PART %s :%s\r\n" % (channel,reason))
		else:
			reply("Access denied, you need the +j (join/part) flag to use this action.", chan, nick)
		return
	if command == "quit":
		if actionlevel[startup] == 0:
				reply("Access denied, you need the +p (power) flag to use this action." % OWNER, chan, nick)
		else:
			try:
				s.send("QUIT :%s\r\n" % ' '.join(line2[4:]))
			except Exception:
				s.send("QUIT\r\n")
			import sys
			sys.exit(1)
		return
	if command == "msg":
		if actionlevel[startup] == 1:
			say(' '.join(line2[5:]), line2[4])
		else:
			reply("Access denied, you need the +s (talk as bot) flag  to use this action.", chan, nick)
		return
	if command == "me":
		if actionlevel[startup] == 1:
			s.send("PRIVMSG "+line2[4]+" ACTION "+ ' '.join(line2[5:]) )
		else:
			reply("Access denied, you need the +s (talk as bot) flag to use this action.", chan, nick)
		return
	if command == "num":
		try:
			params = string.lower(line2[4])
		except Exception:
			params = "spi"
		if params == "abuse":
                        invest = unicode(int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Abuse_response_-_Waiting_for_Investigation&cmlimit=500").read()))))
                        o = unicode(int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:Abuse_response_-_Open&cmlimit=500").read()))))
                        reply("There are currently %s awaiting investigation and %s open investigations." % (invest, o), chan, nick)
                elif params == "spi":
                        try:
                                import time
                                print "Start opening"
                                cur = int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:SPI_requests_for_pre-CheckUser_review&cmlimit=500").read())))
                                time.sleep(.25)
                                cuendorse = int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:SPI_cases_awaiting_a_CheckUser&cmlimit=500").read())))
                                time.sleep(.25)
                                inprogress = int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:SPI_cases_currently_in_progress&cmlimit=500").read())))
                                time.sleep(.25)
                                waitclose = int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:SPI_cases_awaiting_administration&cmlimit=500").read())))
                                time.sleep(.25)
                                close = int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:SPI_cases_pending_close&cmlimit=500").read())))
                                time.sleep(.25)
                                admin = int(len(re.findall("title=", urllib.urlopen("http://en.wikipedia.org/w/api.php?action=query&list=categorymembers&cmtitle=Category:SPI_requests_needing_an_Administrator&cmlimit=500").read())))
                                time.sleep(.25)
                                print "Send Msg"
                                reply("SPI Status: CU Request - %s, CU Endorse - %s, CU in progress - %s, Checked/Open cases - %s, Archive - %s, Need admin - %s" % (cur, cuendorse, inprogress, waitclose, close, admin), chan, nick)
                        except:
                                print traceback.format_exc()
                                return
		return
	if command == "nick":
		if actionlevel[nick] == 1:
			try:
				new_nick = line2[4]
			except Exception:
				reply("Please specify a nick to change to.", chan, nick)
				return
			s.send("NICK %s\r\n" % new_nick)
		else:
			reply("Access denied, you need the +n (nick flag) to use this action.", chan, nick)
		return
	if command == "kick" or command == "ban" or command == "kickban" or command == "unban" or command == "quiet" or command == "unquiet":
                if "spi" in chan:say("op #wikipedia-en-spi LisaBot", "ChanServ")
                try:
                        user = line2[4]
                except Exception:
                        user = nick
                if (command == "kick" or command == "kickban" or command == "ban" or command == "quiet") and (user == "DeltaQuad" or "DQ|" in user or "FAdmArcher" in user):
                        if not host == 'wikipedia/DeltaQuad':
                                reply("Access denied, you are not DeltaQuad.", chan, nick)
                                return
                import time
                time.sleep(1)
                if actionlevel[ban] == 1 and (command == "kick" or command == "ban" or command == "kickban" or command == "unban"):      
                        try:
                                if command == "kick":
                                        s.send("KICK %s %s :%s\r\n" % (chan, line2[4], line2[4]))
                                if command == "ban":
                                        s.send("MODE %s +b %s\r\n" % (chan, line2[4]))
                                if command == "kickban":
                                        s.send("MODE 0%s +b %s\r\n" % (chan, line2[4]))
                                        s.send("KICK %s %s :%s\r\n" % (chan, line2[4], line2[4]))
                                if command == "unban":
                                        s.send("MODE %s -b %s\r\n" % (chan, line2[4]))
                                if command == "unquiet":
                                        s.send("MODE %s -q %s\r\n" % (chan, line2[4]))
                                if command == "quiet":
                                        s.send("MODE %s +q %s\r\n" % (chan, line2[4]))
                                time.sleep(1)
                                if "spi" in chan:say("deop #wikipedia-en-spi LisaBot", "ChanServ")
                        except:
                                if line2[4]:
                                        reply("I do not have sufficienct authorization.", chan, nick)
                                        print traceback.format_exc()
                                        return
                                else:
                                        reply("Please enter a user.", chan, nick)
                                        return
                elif actionlevel[kick] == 1 and (command == "quiet" or command == "unquiet"):      
                        try:
                                if command == "unquiet":
                                        s.send("MODE %s -q %s\r\n" % (chan, line2[4]))
                                if command == "quiet":
                                        s.send("MODE %s +q %s\r\n" % (chan, line2[4]))
                                time.sleep(1)
                                if "spi" in chan:say("deop #wikipedia-en-spi LisaBot", "ChanServ")
                        except:
                                reply("I do not have sufficienct authorization.", chan, nick)
                                print traceback.format_exc()
                                return
                else:
                        reply("Access denied, you need the +b/q (ban/quiet) flag to use this action.", chan, nick)
                        return
        if command == "mode":
                import time
                if actionlevel[mode] == 1:
                        try:
                                if line2[5]:
                                        if "spi" in chan:say("op #wikipedia-en-spi LisaBot", "ChanServ")
                                        if chan == "##DeltaQuadBot":
                                                say("op ##DeltaQuadBot LisaBot", "ChanServ")
                                                time.sleep(1)
                                        s.send("MODE %s %s %s\r\n" % (chan, line2[4], line2[5]))
                                        if chan == "##DeltaQuadBot":
                                                time.sleep(1)
                                                say("deop ##DeltaQuadBot LisaBot", "ChanServ")
                                        if "spi" in chan:say("deop #wikipedia-en-spi LisaBot", "ChanServ")
                        except:
                                if chan == "##DeltaQuadBot":say("op ##DeltaQuadBot LisaBot", "ChanServ")
                                if "spi" in chan:say("op #wikipedia-en-spi LisaBot", "ChanServ")
                                time.sleep(1)
                                s.send("MODE %s %s\r\n" % (chan, line2[4]))
                                time.sleep(1)
                                if "spi" in chan:say("deop #wikipedia-en-spi LisaBot", "ChanServ")
                                if chan == "##DeltaQuadBot":say("deop ##DeltaQuadBot LisaBot", "ChanServ")
                else:
                        reply("Access denied, you need the +m (mode) flag to use this action.", chan, nick)
        if command == "stalk" or command == "unstalk" or command == "hide" or command == "unhide":
                reply("Due to new improvements to the RC system, these commands are currently disabled till they match the upgraded RC system. Please contact DeltaQuad to change what LisaBot stalks.", chan, nick)
                return
                import MySQLdb, traceback
                if command == "stalk":
                        try:
                                db = MySQLdb.connect(db="u_deltaquad_rights", host="sql", read_default_file="/home/deltaquad/.my.cnf")
                                db.query("INSERT INTO rcstalklist (`stalk`, `channel`) VALUES ('%s', '%s');" %(' '.join(line2[4:]), chan))
                                db.commit()
                        except:
                                reply("Error.", chan, nick)
                                print traceback.format_exc()
                if command == "hide":
                        try:
                                db = MySQLdb.connect(db="u_deltaquad_rights", host="sql", read_default_file="/home/deltaquad/.my.cnf")
                                db.query("INSERT INTO rcblacklist (`stalk`, `channel`) VALUES ('%s', '%s');" %(' '.join(line2[4:]), chan))
                                db.commit()
                        except:
                                reply("Error.", chan, nick)
                                print traceback.format_exc()
                if command == "unstalk":
                        try:
                                db = MySQLdb.connect(db="u_deltaquad_rights", host="sql", read_default_file="/home/deltaquad/.my.cnf")
                                db.query("DELETE FROM rcstalklist WHERE stalk = \"%s\" AND channel = \"%s\";" %(' '.join(line2[4:]), chan))
                                db.commit()
                        except:
                                reply("Error.", chan, nick)
                                print traceback.format_exc()
                if command == "unhide":
                        try:
                                db = MySQLdb.connect(db="u_deltaquad_rights", host="sql", read_default_file="/home/deltaquad/.my.cnf")
                                db.query("DELETE FROM rcblacklist WHERE stalk = \"%s\" AND channel = \"%s\";" %(' '.join(line2[4:]), chan))
                                db.commit()
                        except:
                                reply("Error.", chan, nick)
                                print traceback.format_exc()
		return
	if command == "startup":
                if actionlevel[startup] == 1:
                        channel = "#wikipedia-en-abuse-v"
                        s.send("JOIN %s\r\n" % channel)
			channel = "##DeltaQuad-private"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#wikipedia-en-unblock-dev"  
			s.send("JOIN %s\r\n" % channel)
			channel = "##DeltaQuad-RFA"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#everythingfoodanddrink"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#everythingfoodanddrink-mlpearc"  
			s.send("JOIN %s\r\n" % channel)
			channel = "##DeltaQuad-RC-admin"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#wikipedia-en-proxy"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#wikipedia-en-utrs"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#wikipedia-en-unblock-dev"
			s.send("JOIN %s\r\n" % channel)
			channel = "#wikipedia-en-accounts-admins"  
			s.send("JOIN %s\r\n" % channel)
			channel = "#wikipedia-en-proxy"  
			s.send("JOIN %s\r\n" % channel)
			reply("Bot startup complete.", chan, nick)
		else:
			reply("Access denied, you need the +s (startup) flag to use this action.", chan, nick)
		return
	if command == "promote" or command == "demote" or command == "voice" or command == "devoice":
                try:
                        user = line2[4]
                except Exception:
                        user = nick
                if command == "promote":command="op"
                if command == "demote":command="deop"
                if (command == "deop" or command == "devoice") and (user == "DeltaQuad" or "DQ|" in user or "FAdmArcher" in user):
                        if not host == 'wikipedia/DeltaQuad':
                                reply("Access denied, you are not DeltaQuad.", chan, nick)
                                return
                if actionlevel[op] == 1:
                        try:
                                say("%s %s %s" % (command, chan, user), "ChanServ")
                        except:
                                reply("Access denied, you need the +o (operator) flag to use this action.", chan, nick)
                        return
		elif actionlevel[voice] == 1:
                        if not command == "voice" and not command =="devoice":
                                reply("Access denied, you need the +o (operator) flag to use this action.", chan, nick)
                                return
			say("%s %s %s" % (command, chan, user), "ChanServ")
		else:
			reply("Access denied, you need the +v/o (voice/op) flags  to use this action.", chan, nick)
		return
	if command == "trout":
                if True:#actionlevel[trout] == 1:
                        try:
                                user = line2[4]
                                user = ' '.join(line2[4:])
                        except Exception:
                                reply("Hahahahahahahaha...", chan, nick)
                                return
                        normal = unicodedata.normalize('NFKD', unicode(string.lower(user)))
                        if "itself" in normal or "Lisa" in normal or "LisaBot" in normal or "lisa" in normal or "lisabot" in normal:
                                reply("I'm not that stupid ;)", chan, nick)
                                return
                        elif "deltaquad" not in normal and "DeltaQuad" not in normal and "DQ" not in normal and "dq" not in normal and "FAdmArcher" not in normal and "FADMArcher" not in normal and "fadmarcher" not in normal and "DairyQueen" not in normal and "dairyqueen" not in normal:
                                text = 'slaps %s around a bit with a large trout.' % user
                                msg = '\x01ACTION %s\x01' % text
                                say(msg, chan)
                        else:
                                reply("I refuse to hurt anything with \"DeltaQuad\" in its name :P", chan, nick)
                        return
                else:
                        reply("Access denied, you need the +t (trout) flag to use this action.", chan, nick)
                        
	if command == "kill":
		reply("Who do you think I am? The Mafia?", chan, nick)
		return
	if command == "reminder":
                import time
		try:
			times = int(line2[4])
			content = ' '.join(line2[5:])
		except Exception:
			reply("Please specify a time and a note in the following format: !remind <time> <note>.", chan, nick)
			return
		reply("Set reminder for \"%s\" in %s seconds." % (content, times), chan, nick)
		time.sleep(times)
		reply(content, chan, nick)
		return
	if command == "langcode":
		try:
			lang = line2[4]
		except Exception:
			reply("Please specify an ISO code.", chan, nick)
			return
		data = urllib.urlopen("http://toolserver.org/~earwig/cgi-bin/swmt.py?action=iso").read()
		data = string.split(data, "\n")
		result = False
		for datum in data:
			if datum.startswith(lang):
				result = re.findall(".*? (.*)", datum)[0]
				break
		if result:
			reply(result, chan, nick)
			return
		reply("Not found.", chan, nick)
		return
	if command == "geolocate":
                try:
                        say(getGeo(line2[4]), chan)
                except:
                        say("Try a valid IP address.", chan)
	if command == "sql":
                if not actionlevel[permission] == 1:
                        reply("Access denied, you need the +f (permissions) flag to use this action.", chan, nick)
                        return
                try:
			action = line2[4]
		except BaseException:
			reply("What do you want me to do?", chan, nick)
			return
                import MySQLdb
		db = MySQLdb.connect(db="u_deltaquad_rights", host="sql", read_default_file="/home/deltaquad/.my.cnf")
		try:reqchan = str(line2[5])
                except:
                        reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                        return
		try:cloak = str(line2[6])
		except:
                        reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                        return
		if action == "read":
                        if " " in cloak: cloak = string.split(cloak, " ")[0]
                        if not cloak or "\"" in cloak:
                                reply("Please include the name of the entry you would like to read after the command.", chan, nick)
                                return
                        try:
                                channew = chan
                                db.query("SELECT * FROM accessnew WHERE cloak = \"%s\" AND channel = \"%s\";" % (cloak,reqchan))
                                r = db.use_result()
                                entry = r.fetch_row()
                                print "entry: " + ' '.join(str(entry[0][0:]))
                                ####for entry in data:
                                cloak = entry[0][0]
                                channel=entry[0][1]
                                #s added to all commands because without 's' is already defined
                                ops=entry[0][2]
                                voices=entry[0][3]
                                bans=entry[0][4]
                                kicks=entry[0][5]
                                globalmsgs=entry[0][6]
                                startups=entry[0][7]
                                quiets=entry[0][8]
                                nicks=entry[0][9]
                                modes=entry[0][10]
                                trouts=entry[0][11]
                                permissions=entry[0][12]
                                restarts=entry[0][13]
                                joinparts=entry[0][14]
                                blockeds=entry[0][15]
                                notice(nick, "Entry \"\x02%s\x0F\": Channel: %s Ops: %s Voice: %s Ban: %s Kick: %s Globalmsg: %s Startup: %s Nick: %s  Quiet: %s Mode: %s Trout: %s Permission: %s Restart: %s Join/part: %s Blocked: %s" % (cloak, channel, ops, voices, bans, kicks, globalmsgs, startups, quiets, nicks, modes, trouts, permissions, restarts, joinparts, blockeds))
                        except Exception:
                                import traceback
                                print traceback.format_exc()
                                reply("There is no cloak titled \"\x02%s\x0F\"." % cloak, chan, nick)
                        return                
                elif action == "del":
                        if not cloak or "\"" in cloak:
                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                                return
                        if "#" not in reqchan or "@" not in cloak:
                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                        try:
                                db.query("DELETE FROM accessnew WHERE cloak = \"%s\" AND channel = \"%s\";" % (cloak, reqchan))
                                db.commit()
                                reply("Done if any were present.", chan, nick)
                        except Exception:
                                print traceback.format_exc()
                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)                
                elif action == "modify":
                        reqchan = str(line2[5])
                        cloak = str(line2[6])
                        field = str(line2[7])
                        try:value =  str(line2[8])
                        except:a=1
                        if not cloak or "\"" in cloak:
                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                                return
                        if "#" not in reqchan or "@" not in cloak:
                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                        if field.lower() == "@voice":
                                try:
                                        db.query("UPDATE accessnew SET voice=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET trout=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.commit()
                                        reply("Done!", chan, nick)
                                        return
                                except Exception:
                                        print traceback.format_exc()
                                        reply("There is no cloak titled \"\x02%s\x0F\"." % cloak, chan, nick)
                        if field.lower() == "@ops":
                                try:
                                        db.query("UPDATE accessnew SET voice=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET op=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET ban=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET quiet=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET trout=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET joinpart=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.commit()
                                        reply("Done!", chan, nick)
                                        return
                                except Exception:
                                        print traceback.format_exc()
                                        reply("There is no cloak titled \"\x02%s\x0F\"." % cloak, chan, nick)
                        if field.lower() == "@mode":
                                try:
                                        db.query("UPDATE accessnew SET voice=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET op=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET ban=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET quiet=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET trout=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET joinpart=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan))
                                        db.query("UPDATE accessnew SET mode=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan)) 
                                        db.commit()
                                        reply("Done!", chan, nick)
                                        return
                                except Exception:
                                        print traceback.format_exc()
                                        reply("There is no cloak titled \"\x02%s\x0F\"." % cloak, chan, nick)                        
                        try:
                                db.query("UPDATE accessnew SET %s=\'%s\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (field, value, cloak, reqchan))
                                db.commit()
                                reply("Done!", chan, nick)
                                return
                        except Exception:
                                print traceback.format_exc()
                                reply("There is no cloak titled \"\x02%s\x0F\"." % cloak, chan, nick)
                        return
                elif action == "add":
                        reqchan = str(line2[5])
                        cloak = str(line2[6])
                        field = str(line2[7])
                        try:value =  str(line2[8])
                        except:a=1
                        try:
                                if line2[5] == "@global":
                                        channew = "@global"
                                        db.query("SELECT * FROM accessnew WHERE cloak = \"%s\" AND channel = \"@global\";" % cloak)
                                else:
                                        channew = chan
                                        db.query("SELECT * FROM accessnew WHERE cloak = \"%s\ AND channel = \"%s\";" % (cloak,reqchan))
                                r = db.use_result()
                                data = r.fetch_row()
                                print data[0][5]
                                reply("There is already a entry under that cloak, please use the modify command." % specify, chan, nick)
                                return
                        except:a=1
                        if not cloak or "\"" in cloak:
                                reply("Invalid command", chan, nick)
                                return
                        if "#" not in reqchan or "@" not in cloak:
                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                        try:
                                if field.lower() == "@voice":
                                        db.query("INSERT INTO accessnew (`cloak`, `channel`, `voice`) VALUES ('%s', '%s', '1');" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET trout=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.commit()
                                        reply("Done!", chan, nick)
                                        return
                                if field.lower() == "@ops":
                                        db.query("INSERT INTO accessnew (`cloak`, `channel`, `voice`) VALUES ('%s', '%s', '1');" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET trout=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET op=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET ban=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET kick=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET quiet=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.commit()
                                        reply("Done!", chan, nick)
                                        return
                                if field.lower() == "@mode":
                                        db.query("INSERT INTO accessnew (`cloak`, `channel`, `voice`) VALUES ('%s', '%s', '1');" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET trout=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET op=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET ban=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET kick=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET quiet=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.query("UPDATE accessnew SET mode=\'1\' WHERE cloak=\'%s\' AND channel=\'%s\';" % (cloak, reqchan) )
                                        db.commit()
                                        reply("Done!", chan, nick)
                                        return
                                else:
                                        try:
                                                db.query("INSERT INTO accessnew (`cloak`, `channel`, `%s`) VALUES ('%s', '%s', '%s');" % (field, cloak, reqchan, value) )
                                                db.commit()
                                                reply("Done!", chan, nick)
                                        except:
                                                reply("Your mode operator is incorrect, please consult the perms manual!", chan, nick)
                                        return
                        except Exception:
                                reply("Error.", chan, nick)
                                print traceback.format_exc()
                        return
def getGeo(ip):#,loc):
        # Copyright (c) 2010, Westly Ward
        # All rights reserved.
        #
        # Redistribution and use in source and binary forms, with or without
        # modification, are permitted provided that the following conditions are met:
        # * Redistributions of source code must retain the above copyright
        # notice, this list of conditions and the following disclaimer.
        # * Redistributions in binary form must reproduce the above copyright
        # notice, this list of conditions and the following disclaimer in the
        # documentation and/or other materials provided with the distribution.
        # * Neither the name of the pyipinfodb nor the
        # names of its contributors may be used to endorse or promote products
        # derived from this software without specific prior written permission.
        #
        # THIS SOFTWARE IS PROVIDED BY Westly Ward/DeltaQuad ''AS IS'' AND ANY
        # EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
        # WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
        # DISCLAIMED. IN NO EVENT SHALL Westly Ward BE LIABLE FOR ANY
        # DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
        # (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
        # LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
        # ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
        # (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
        # SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
        import urllib,urllib2,json
        """Same as GetCity and GetCountry, but a baseurl is required. This is for if you want to use a different server that uses the the php scripts on ipinfodb.com."""
        passdict = {"output":"json", "key":KEY, "timezone":"true", "ip":ip}
        urldata = urllib.urlencode(passdict)
        baseurl = "http://api.ipinfodb.com/v2/ip_query.php"
        url = str(baseurl) + "?" + str(urldata)
        urlobj = urllib2.urlopen(url)
        data = urlobj.read()
        urlobj.close()
        datadict = json.loads(data)
        info = datadict
        #END
        if not info["Status"] == "OK":
                return "Try a valid IP address"
        #if loc:
                #return "Long: " + str(info["Longitude"]) + " Lat: " + str(info["Latitude"]) + "."
        if str(info["City"]) == "":
               info["City"] == "Unknown"
        if str(info["RegionName"]) == "":
               info["City"] == "Unknown"
        return "Estimated Location for "+str(info['Ip'])+" : " + str(info["City"]) + ", "+ str(info["RegionName"]) + ", "+ str(info["CountryName"]) + ". Timezone: "+ str(info["TimezoneName"])

def blockinfo(IP):
        import urllib,urllib2,json,re
        test = re.search("(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)",IP)
        if test == None:#user
            passdict = {"action":"query", "list":"blocks", "bkprop":"id|user|by|timestamp|expiry|reason|range|flags", "bklimit":"1","bkusers":IP}
        else:#ip
            passdict = {"action":"query", "list":"blocks", "bkprop":"id|user|by|timestamp|expiry|reason|range|flags", "bklimit":"1","bkip":IP}
        urldata = urllib.urlencode(passdict)
        baseurl = "http://en.wikipedia.org/w/api.php"
        url = str(baseurl) + "?" + str(urldata)
        urlobj = urllib2.urlopen(url)
        json = urlobj.read()
        urlobj.close()
        try:json = json.split("<span style=\"color:blue;\">&lt;blocks&gt;</span>")[1]
        except:return "User is not blocked."
        json = json.split("<span style=\"color:blue;\">&lt;/blocks&gt;</span>")[0]
        json = json.split("<span style=\"color:blue;\">&lt;")[1]
        json = json.replace("&quot;","\"")
        bid=json.split("block id=\"")[1]
        bid=bid.split("\"")[0]
        gen="Block " + str(bid)
        bid=json.split("user=\"")[1]
        bid=bid.split("\"")[0]
        gen=gen+" targeting " + str(bid)
        bid=json.split("by=\"")[1]
        bid=bid.split("\"")[0]
        gen=gen+" was blocked by " + str(bid)
        bid=json.split("timestamp=\"")[1]
        bid=bid.split("\"")[0]
        gen=gen+" @" + str(bid)
        bid=json.split("expiry=\"")[1]
        bid=bid.split("\"")[0]
        gen=gen+" and expires at " + str(bid)
        bid=json.split("reason=\"")[1]
        bid=bid.split("\"")[0]
        gen=gen+" because \"" + str(bid) + "\" ("
        gen = gen.replace("&amp;lt;","<")
        gen = gen.replace("&amp;gt;",">")
        if "nocreate" in json:
            gen = gen + "Account Creation Blocked, "
        if "anononly" in json:
            gen = gen + "Anonomous Users Only, "
        else:
            gen = gen + "Hardblocked, "
        if not "allowusertalk" in json:
            gen = gen + "User Talk Page REVOKED)"
        else:
            gen = gen + "User Talk Page allowed)"
        return gen
