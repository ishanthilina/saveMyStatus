#!/usr/bin/env python

#Save My Status:
#
#About:
#This script will load the last used status when empathy restarts or
#when one of the accounts of the user comes online.
#
#How to use this:
#(These guidelines are for Ubuntu 11.04 . But procedure will be lot common
#in other Linux flavours too)
#
# 1).Create a folder named ".scripts" in the home directory. Copy this script to that folder.
# 2).Go to Startup Application Preferences (search for "startup" in dashboard).
# 3).Click Add.
# 4).Give any Name you like.
# 5).In Command, click on Browse and select your script from the file browser (which is in
#    /home/<Your user name>/.scripts)
# 6).Add a comment if you like.
#
# Now the script will run from the next time you login to the computer. Have fun. And don't forget to give me feedback :-). 

#
#Author: Ishan Thilina Somasiri
#E-mail: ishan@ishans.info
#Version: 1
#Release date: 12th Oct 2011
#





import dbus, gobject
from dbus.mainloop.glib import DBusGMainLoop
import ConfigParser
import time,sys


#####
#D-bus data
#####

# # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #
# All constants below were taken from 
#https://github.com/engla/kupfer/blob/master/kupfer/plugin/empathy.py

ACCOUNTMANAGER_PATH = "/org/freedesktop/Telepathy/AccountManager"
ACCOUNTMANAGER_IFACE = "org.freedesktop.Telepathy.AccountManager"
ACCOUNT_IFACE = "org.freedesktop.Telepathy.Account"
SIMPLE_PRESENCE_IFACE = "org.freedesktop.Telepathy.Connection.Interface.SimplePresence"
DBUS_PROPS_IFACE = "org.freedesktop.DBus.Properties"


def status_handler(args):
    
    for data in args.iteritems():
        ##################################################
        #This if condition block handles presence/status updates
        ##################################################
        if data[0]=='CurrentPresence':
            
            #Skip this status update if it's a initialization message. The initialization message
            #sets the initial presence to 'Available'. This is not what we want. So we skip that 
            #status update
            if args.get('Nickname'):
                continue
            
            presence=data[1][1]
            status=data[1][2]
            
            #We don't need to save offline as a status...!
            if presence!='offline':
                
                
                #presist the current status
                config = ConfigParser.RawConfigParser()
                config.add_section('Status')
                config.set('Status','presence',data[1][1])
                config.set('Status','status',data[1][2])
                
                # Writing our configuration file
                with open('./CurrentStatus.cfg', 'wb') as configfile:
                    config.write(configfile)
                    print "written"
         
        ################################        
        #End of status/presence handling
        ################################
        
        ###############################################################
        #This if condition block is responsible for handling the status 
        #of an account when an account comes online 
        ###############################################################
        if data[0]=='ConnectionStatus':
       
            #data[1]==0 if the account has come online
            #data[1]==1 if the account is in the connecting state
            #data[1]==2 if the account is online
            if data[1]==0:
                
                
                config = ConfigParser.RawConfigParser()
                
                try:
                    open('CurrentStatus.cfg')
                except IOError:
                    print "file not found"
                    sys.exit()
                
                
                config.read('CurrentStatus.cfg')
                presence=config.get('Status','presence' )
                status=config.get('Status','status' )
                
  
                bus = dbus.SessionBus()
    
                #####################################################################
                #The following code was derived from
                #https://github.com/engla/kupfer/blob/master/kupfer/plugin/empathy.py 
                
                proxy_obj = bus.get_object(ACCOUNTMANAGER_IFACE, ACCOUNTMANAGER_PATH)
                interface = dbus.Interface(proxy_obj, DBUS_PROPS_IFACE)
                
                for valid_account in interface.Get(ACCOUNTMANAGER_IFACE, "ValidAccounts"):
                    account = bus.get_object(ACCOUNTMANAGER_IFACE, valid_account)
                    connection_status = account.Get(ACCOUNT_IFACE, "ConnectionStatus")
                    
                    if connection_status != 0:
                        continue
                    
                    connection_path = account.Get(ACCOUNT_IFACE, "Connection")
                    connection_iface = connection_path.replace("/", ".")[1:]
                    connection = bus.get_object(connection_iface, connection_path)
                    simple_presence = dbus.Interface(connection, SIMPLE_PRESENCE_IFACE)
                    simple_presence.SetPresence(presence, status)
                

    
    


dbus.mainloop.glib.DBusGMainLoop(set_as_default=True)
bus = dbus.SessionBus()

bus.add_signal_receiver(status_handler, "AccountPropertyChanged", "org.freedesktop.Telepathy.Account",None,None)

loop = gobject.MainLoop()
loop.run()
