---
layout: post
title: "Raspberry Pi Init Script for a Python Program"
description: "A sysvinit script for Raspbian OS to run a Python program"
category: articles
tags: [GPIO, operations, python, raspberry pi, raspbian, software]
comments: true
---

## Raspberry Pi Init Script
Have you written something handy on your Raspberry Pi and want it to run when the Pi boots up?  Making this happen with the Raspbian init system is more difficult than it should be, especially if you want your program to exit correctly and log stdout to a file of your choosing.

This example init script uses the [SysVinit](http://en.wikipedia.org/wiki/Init#SysV-style) system currently utilized by the Raspbian operating system and controls a Python program that runs as root (`sudo` required because GPIO pins are used).  The init script takes care of starting the program when the Pi starts, gracefully stopping when told to, and logging to a file without [buffering](http://www.pixelbeat.org/programming/stdio_buffering/).  All this with only a few additional lines of Python to handle the [TERM signal](http://man7.org/linux/man-pages/man7/signal.7.html) when told to stop.

_Please note_: One of the design goals of this init script was to [daemonize](http://en.wikipedia.org/wiki/Daemon_%28computing%29) the Python program with as few modifications to the program as possible.  If you are designing a program for distribution, you'll want the program to handle stdout and stderr with proper logging instead of redirection within the init script.

## The SysVInit Script
This example script is from my [Ship-It](https://github.com/lanyonm/ship-it) project.  Let's have a look at the entire script before dissecting it:
{% highlight bash linenos %}
#!/bin/sh
#
# init script for ship-it
#

### BEGIN INIT INFO
# Provides:          ship-it
# Required-Start:    $remote_fs $syslog $network
# Required-Stop:     $remote_fs $syslog $network
# Default-Start:     2 3 4 5
# Default-Stop:      0 1 6
# Short-Description: init script for the ship-it box
# Description:       We'll have to fill this out later...
### END INIT INFO

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
NAME=ship-it
DAEMON=/home/pi/ship-it/main.py
DAEMONARGS=""
PIDFILE=/var/run/$NAME.pid
LOGFILE=/var/log/$NAME.log

. /lib/lsb/init-functions

test -f $DAEMON || exit 0

case "$1" in
    start)
        start-stop-daemon --start --background \
            --pidfile $PIDFILE --make-pidfile --startas /bin/bash \
            -- -c "exec stdbuf -oL -eL $DAEMON $DAEMONARGS > $LOGFILE 2>&1"
        log_end_msg $?
        ;;
    stop)
        start-stop-daemon --stop --pidfile $PIDFILE
        log_end_msg $?
        rm -f $PIDFILE
        ;;
    restart)
        $0 stop
        $0 start
        ;;
    status)
        start-stop-daemon --status --pidfile $PIDFILE
        log_end_msg $?
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 2
        ;;
esac

exit 0
{% endhighlight %}

The comments on lines 6-14 are used by SysVinit to determine when during the boot process the script should be called (they're not just comments). The script uses [`start-stop-daemon`](http://man7.org/linux/man-pages/man8/start-stop-daemon.8.html), a handy daemon control utility available on Debian and therefore Raspbian systems.  There are several key pieces:

* `--pidfile $PIDFILE` tells start-stop-daemon to use a pidfile (the process id of the daemon) to determine what action to take.  This is key to the usefulness of start-stop-daemon because it can read the pidfile and check for the existence of the process.  If you've just asked start-stop-daemon to start an instance of the program but one already exists, start-stop-daemon will tell you "process already running".  If you ask the start-stop-daemon to stop, it will send a TERM signal to the process id in the pidfile.
* `--make-pidfile` tells start-stop-daemon to create a pidfile if one hasn't already been created.
* Unbuffered logging.  This is achieved by using `stdbuf` from the exec'd bash shell and telling it to use line buffer mode.  This means that instead of waiting for a certain size of log information to be generated before saving it to the log file, each line will be written to the file as the program produces it.
* Pidfile cleanup.  Line 37 removes the pidfile after the daemon exits.  If your Python program doesn't exit when the TERM signal is sent, this file will still be removed - so be sure that your program terminates correctly when it receives the TERM signal.  More on this below.

Why all this complexity?  For the output redirection and unbuffered logging.  Without lots of logging code _within_ the Python program, things get messy when you try to daemonize a process.  The use of `--startas /bin/bash` allows the redirection of stdout and stderr to a file via the exec'd bash process.  Because we have a Python program exec'd from bash, bash buffers the output before writing to the log.  Using `stdbuf` allows us to set the buffing configuration of the process.  It feels messy, but allows a simple program to function as expected.

## Flexibility
The bash variables on lines 17-21 should provide the flexibility to reuse the init script without any edits to the _logic_ of the script.  It would be possible to reuse this script without changing anything below line 20.

## Python to Handle the TERM Signal
In order for the Python program to exit gracefully when the TERM signal is received, it must have a function that exits the program when `signal.SIGTERM` is received.  The function is assigned to a signal handler as seen here:

{% highlight python %}
def sigterm_handler(_signo, _stack_frame):
    "When sysvinit sends the TERM signal, cleanup before exiting."
    print("[" + get_now() + "] received signal {}, exiting...".format(_signo))
    cleanup_pins()
    sys.exit(0)

signal.signal(signal.SIGTERM, sigterm_handler)
{% endhighlight %}

As mentioned above, this Python program uses the GPIO pins.  These pins must be cleaned up so the next program instance can initialize them cleanly.  Catching the TERM signal allows `GPIO.cleanup()` to be called (and a message logged) before the program exits.  If you view the [full program](https://github.com/lanyonm/ship-it/blob/master/main.py) you'll see that the main loop will also catch a `KeyboardInterrupt` and cleanup the GPIO pins before exiting.

## Installation
SysVinit scripts go into the `/etc/init.d` folder and are linked to from the `/etc/rc*` directories.  The numbered directories represent different runlevels (also seen on lines 10-11 of the init script).  Assuming the script is called `ship-it.sh` and it's currently in the `pi` user's home directly, here's the installation process:

{% highlight bash %}
$ sudo cp /home/pi/ship-it.sh /etc/init.d/ship-it
$ sudo chmod +x /etc/init.d/ship-it
$ sudo update-rc.d ship-it defaults
{% endhighlight %}

## Usage
With our SysVinit script installed, we are able to use the [`service`](http://manpages.debian.org/cgi-bin/man.cgi?query=service) command to interact with it.  Use `sudo service ship-it status` to see the status of the daemon.  To start the program: `sudo service ship-it start`.  To stop the program: `sudo service ship-it stop`.

If you attempt to start the program after an instance has already been started, you'll see something like the following:

{% highlight bash %}
pi@pecan-pi ~ $ sudo service ship-it start
. ok
pi@pecan-pi ~ $ sudo service ship-it start
process already running.
 failed!
{% endhighlight %}

This is referred to as idempotence, a term borrowed from mathematics.  In computer science it means that repeating an operation will not change or duplicate the result beyond the effect of the initial operation.  This is critically important for this init script because you wouldn't want multiple instances of the Python program running at once.

## Other Considerations
If the daemon is running for a long time, it is possible that the log file size will become untenable.  There are several methods to handle this, but I'd recommend [logrotate](http://linuxcommand.org/man_pages/logrotate8.html).  If you choose to add logrotation, you'll want to also change the stdout and stderr redirection to appending (`>>`) instead of overwriting (`>`) on line 31 of the init script.

Happy hacking!
