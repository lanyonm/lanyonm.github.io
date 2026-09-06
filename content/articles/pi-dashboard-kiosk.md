---
title: "Raspberry Pi Dashboard Kiosk"
description: "How to create a Raspberry Pi based dashboard kiosk"
date: 2013-05-31
tags: [data visualization, kiosk, raspberry pi, raspbian, software]
comments: true
aliases:
  - "/articles/2013/05/31/pi-dashboard-kiosk.html"
---

<style type="text/css">h2 { margin: 1em 0; }</style>

I've had a Raspberry Pi sitting on my desk at home for months telling me whether I had new Gmail.  At $35, the Pi is cheap, but I sure wasn't getting my money's worth using it as a glorified dock notification.  Then I saw [this post](http://pivotallabs.com/using-a-raspberry-pi-as-an-information-radiator/) from Pivotal Labs about using a Pi as a kiosk.  I immediately thought of using a Pi to display Graphite graphs at work, and while it took an ashamedly long time to get moving on the project, the configuration only took an hour.

_Update 2015-02-25_: As of the [2015-01-31 release](http://downloads.raspberrypi.org/raspbian/release_notes.txt) of Raspbian (for Pi2 support), the LXDE `autostart` file is located at `/etc/xdg/lxsession/LXDE-pi/autostart`.  I've updated the instructions to reflect this change.

<div class="center">
  <figure>
    {{< figure src="/images/pi-kiosk.jpg" link="/images/pi-kiosk.jpg" alt="pi kiosk" >}}
    <figcaption>The full setup - with the Pi exposed.</figcaption>
  </figure>
</div>

Configuring the Pi to be a kiosk was pretty easy.  The idea is to have the Pi boot to a full-screen browser that loads a predetermined page.  Additionally, I installed VNC so that I could view the desktop remotely if necessary.

I followed the following steps starting from a fresh Raspbian image:

Use raspi-config to:

* enable ssh
* change the locale and timezone
* boot to desktop
* expand_rootfs

Update and install some software:
```bash
$ sudo apt-get update
$ sudo apt-get install ttf-mscorefonts-installer unclutter x11vnc x11-xserver-utils
```

Disable sleep so the screen stays on:
```bash
$ sudo vi /etc/lightdm/lightdm.conf

# add the following lines to the [SeatDefaults] section

# don't sleep the screen
xserver-command=X -s 0 dpms
```

Configure LXDE to start the Midori browser on login:
```bash
$ sudo vi /etc/xdg/lxsession/LXDE-pi/autostart

# comment everything and add the following lines

@xset s off
@xset -dpms
@xset s noblank
@midori -e Fullscreen -a http://example.com
```

_Please Note_: If the `LXDE-pi` folder doesn't exist on your, you may be using an earlier version of Raspbian.  The correct location for the pre-2015 Raspbian is `/etc/xdg/lxsession/LXDE/autostart`.

Configure VNC to start on boot
```bash
$ sudo curl -L -o /etc/init.d/x11vnc https://raw.githubusercontent.com/starlightmedia/bin/master/x11vnc
$ sudo chmod 755 /etc/init.d/x11vnc
$ sudo update-rc.d x11vnc defaults
```

## Chromium
If you prefer to use Chrome as the kiosk's browser, you can do this:
```bash
$ sudo apt-get install chromium
```
and:
```bash
$ sudo vi /etc/xdg/lxsession/LXDE-pi/autostart

# replace the midori line with the following
@chromium --kiosk --disable-session-crashed-bubble --disable-restore-background-contents --disable-new-tab-first-run --disable-restore-session-state http://example.com
```

## Refreshes
The Graphite dashboard pictured at the top of this article seemed to have a memory leak because both Midori and Chrome would crash after running the dashboard for about 20 hours.  Instead of trying to fix Graphite I treated the symptoms. [Xdotool](http://www.semicomplete.com/projects/xdotool/) is one of the handy utilities written by the awesome [Jordan Sissel](https://twitter.com/jordansissel) and allows you to simulate keyboard and mouse input.
```bash
sudo apt-get install xdotool
```

and add the following to crontab (you'll need to make sure the `name` matches the browser application you're running):

```bash
0 */6 * * * DISPLAY=:0 xdotool search --name chromium windowactivate --sync key F5
```


That should be all you need to do to get the Pi configured.  I use [RealVNC](http://www.realvnc.com/download/viewer/) to connect to the Pi.

If I've left something out, please leave a comment and let me know.
