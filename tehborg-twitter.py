#!/usr/bin/python

import socket
import tweepy

# teh borg twitter auth
consumer_key=""
consumer_secret=""
access_token=""
access_token_secret=""

# authenticate
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

# irc details
network = 'irc.freenode.net'
port = 6667
channel = '#asciipr0n'
nick = 'tbrg_'

irc = socket.socket ( socket.AF_INET, socket.SOCK_STREAM )
irc.connect ( ( network, port ) )
print irc.recv ( 4096 )
irc.send ( 'NICK ' + nick + '\r\n' )
irc.send ( 'USER ' + nick + ' ' + nick + ' ' + nick + ' :' + nick + '\r\n' )
irc.send ( 'JOIN ' + channel + '\r\n' )

# main loop for scanning and tweeting
while True:
   data = irc.recv ( 4096 )
   if data.find ( 'PING' ) != -1:
      irc.send ( 'PONG ' + data.split() [ 1 ] + '\r\n' )
   if data.find ( '!tb_ quit' ) != -1:
      irc.send ( 'QUIT\r\n' )
   if data.find ( 'KICK' ) != -1:
      irc.send ( 'JOIN ' + channel + '\r\n' )
   if data.find ( 'teh-borg!~borg@asciipr0n.com PRIVMSG' ) != -1:
      data = data.partition(' :')
      api.update_status(data[2])
   print data
