---
layout: post
title: "Raspberry Pi Dashboard Kiosk"
description: "How to create a Raspberry Pi based dashboard kiosk"
category: articles
tags: [data visualization, kiosk, raspberry pi, software]
comments: true
---

I've had a Raspberry Pi sitting on my desk at home for months telling me whether I had new Gmail.  At $35, the Pi is cheap, but I sure wasn't getting my money's worth using it as a glorified dock notification.  Then I saw [this post](http://pivotallabs.com/using-a-raspberry-pi-as-an-information-radiator/) from Pivotal Labs about using a Pi as a kiosk.  I immediately thought of using a Pi to display Graphite graphs at work, and while it took an ashamedly long time to get moving on the project, the configuration only took an hour.

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/pi-kiosk.jpg"><img src="{{ site.url }}/images/pi-kiosk.jpg"></a>
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
{% highlight bash %}
$ sudo apt-get update
$ sudo apt-get install ttf-mscorefonts-installer unclutter x11vnc x11-xserver-utils
{% endhighlight %}

Disable sleep so the screen stays on:
{% highlight bash %}
$ sudo nano /etc/lightdm/lightdm.conf

# add the following lines to the [SeatDefaults] section

# don't sleep the screen
xserver-command=X -s 0 dpms
{% endhighlight %}

Configure LXDE to start the Midori browser on login:
{% highlight bash %}
$ sudo vi /etc/xdg/lxsession/LXDE/autostart

# comment everything and add the following lines

@xset s off
@xset -dpms
@xset s noblank
@midori -e Fullscreen -a http://example.com
{% endhighlight %}

Configure VNC to start on boot
{% highlight bash %}
$ sudo curl -o /etc/init.d/x11vnc https://raw.github.com/starlightmedia/bin/master/x11vnc
$ sudo chmod 755 /etc/init.d/x11vnc
$ sudo update-rc.d x11vnc defaults
{% endhighlight %}

That should be all you need to do to get the Pi configured.  I use [RealVNC](http://www.realvnc.com/download/viewer/) to connect to the Pi.

If I've left something out, please leave a comment and let me know.
