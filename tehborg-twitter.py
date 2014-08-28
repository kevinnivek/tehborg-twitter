#!/usr/bin/python

import socket
import tweepy
import sys, string, os, platform, time, errno
import ConfigParser

# Get config variables
Config = ConfigParser.ConfigParser()
Config.read(os.path.expanduser('~/.tehborg'))

# Function to map configuration sections
def ConfigSectionMap(section):
    dict1 = {}
    options = Config.options(section)
    for option in options:
        try:
            dict1[option] = Config.get(section, option)
            if dict1[option] == -1:
                DebugPrint("skip: %s" % option)
        except:
            print("exception on %s!" % option)
            dict1[option] = None
    return dict1

# Grab actual variables from config file
consumer_key = ConfigSectionMap("twitter")['consumer_key']
consumer_secret = ConfigSectionMap("twitter")['consumer_secret']
access_token = ConfigSectionMap("twitter")['access_token']
access_token_secret = ConfigSectionMap("twitter")['access_token_secret']
host = ConfigSectionMap("irc")['host']
port = int(ConfigSectionMap("irc")['port'])
chan = '#' + ConfigSectionMap("irc")['chan']
nick = ConfigSectionMap("irc")['nick']
ident = ConfigSectionMap("irc")['ident']
realname = ConfigSectionMap("irc")['realname']

# authenticate
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# Our IRC connection
irc = socket.socket()
irc.settimeout(300)
connected = False

def connection(host, port, nick, ident, realname, chan):
    global connected
    while connected is False:
        try:
            irc.connect((host, port))
            time.sleep(10)
            irc.send("NICK %s\r\n" % nick)
            irc.send("USER %s %s bla :%s\r\n" % (ident, host, realname))
            irc.send("JOIN :%s\r\n" % chan)
            connected = True
        except socket.error as e:
        #except Exception as e:
            print "Error : " + str(e)
            continue 

# main definition + loop for scanning and tweeting
def main():
    global connected, host, port, nick, ident, realname, chan
    while connected:
        try:
            data = irc.recv ( 4096 )
            if len(data) == 0:
                close()
                break
            if data.find ( "Nickname is already in use" ) != -1:
                nick = nick + str(time.time())
            if data.find ( 'KICK' ) != -1:
                irc.send ( 'JOIN ' + chan + '\r\n' )
            # Ping Pong so we don't get disconnected
            if data.find ( 'PING' ) != -1:
                irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
            if data.find ( '!tb_quit' ) != -1:
                irc.send ( 'QUIT\r\n' )
                close()
                break
            if data.find ( 'teh-borg!~borg@asciipr0n.com PRIVMSG' ) != -1:
                data = data.partition(' :')
                tweet = data[2]
                try:
                    api.update_status(tweet[:140])
                except Exception, e:
                    print "Error: " + str(e) 
            print data
        except socket.timeout as e :
                close()
                break
    connection(host, port, nick, ident, realname, chan)
    main()

def close():
    try:
        global irc
        irc.shutdown(socket.SHUT_RDWR)
        irc = socket.socket()
        global connected
        connected = False
    except Exception, e:
        print "Error: " + str(e) 

# main calls
connection(host, port, nick, ident, realname, chan)
main()
