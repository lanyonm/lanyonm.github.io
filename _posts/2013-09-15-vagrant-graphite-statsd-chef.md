---
layout: post
title: "Graphite & StatsD in Vagrant with Chef"
description: "A definition for building a Graphite and StatsD server in Vagrant with Chef"
category: articles
tags: [chef, graphite, statsd, vagrant]
comments: true
---

# TL;DR
I created a Vagrantfile and Cheffile to allow quick and easy creation of a Graphite and StatsD server.  You can find the [Gist here](https://gist.github.com/LanyonM/6968660).  Assuming you have the following installed: Vagrant 1.3+, Ruby 1.9+ and the `librarian-chef` gem, you should be able to run the following commands from the folder containing the `Vagrantfile` and `Cheffile` from the gist:

{% highlight bash %}
$ librarian-chef install
$ vagrant plugin install vagrant-vbguest
$ vagrant plugin install vagrant-omnibus
$ vagrant up
{% endhighlight %}

You should see Vagrant download the box, install Guest Additions, install Omnibus Chef, and provision the Vagrant box.  If you encounter problems, let me know so I can add whatever I left out.

# Why?
I like graphs - no really, I *really* do.  [Graphite](http://graphite.wikidot.com/) provides a fantastic way to collect metrics and has a passable dashboard creator.  [StatsD](https://github.com/etsy/statsd/) can be used as a buffering and aggregating proxy for Graphite.  [Vagrant](http://www.vagrantup.com/) is the best thing since sliced bread in the local virtual machine management realm.  There are plenty of articles that about each of these tools, so follow the links (or Google them) if you're interested in learning more.

Another point I want to make clear is that while I use an Ubuntu 12.04 64-bit VirtualBox Vagrant box, because the box is provisioned with a configuration management tool (Chef in this case), these could easily have been changed to CentOS 6.4 or a VMWare image.

# How - the Chef Parts
I'm not going to try to explain Chef in detail, but let's just say that it provides an abstraction layer that allows you to address varied systems in a uniform way.  The definition for installing something (like Java or Vim) is encapsulated into a *recipe*.  Multiple recipes for installing the same thing are typically rolled up into a single *cookbook*.  An example of this would be installing Apache from src or from a package.  Both those recipes would be in the Apache cookbook.

Take it a few steps further and you can define how to install Graphite and StatsD on a server and configure them they way you'd like.  A given cookbook can include recipes from other cookbooks.  For example, the StatsD cookbook installs NodeJs.

[Librarian-Chef](https://github.com/applicationsonline/librarian-chef) provides a way to resolve your cookbook dependencies based on a Cheffile.  Here's my Cheffile:

{% gist 6968660 Cheffile %}

It's pretty straightforward.  The DSL allows for pretty much anything I've ever wanted to do.

# How - the Vagrant Parts
Like I said, Vagrant is the best thing since sliced bread.  The Vagrant website does a great job of explaining it, so I won't do any of that.  My `Vagrantfile` does several things:

* Specifies which Vagrant box to build upon
* Maps some ports
* Tells the guest VM to attempt to bridge to the host's network
* Sets the memory allocation to 1GB
* Installs Chef 11.6.0 via the Omnibus packaging
* Installs VirtualBox Guest Additions
* Installs Vim
* Installs Graphite and configures it to listen for all traffic to port 2003
* Installs StatsD

Before I get into any of the details, here's the code:

{% gist 6968660 Vagrantfile %}

The code above shows how to override some cookbook attributes as well as how to set ports to forward UDP instead of TCP.  If you have any questions, please leave a comment.

# Piece Of Mind
Another thing to mention about Vagrant and Chef is that they allow you to create and destroy VMs reliably and reproducibly.  If the server were to fail and become irrecoverable, I can use this *code that defines infrastructure* to build a new one without expending any cognitive effort.  Obviously it won't recover or replace your data, but Vagrant never purported to being a backup system.   ;)
