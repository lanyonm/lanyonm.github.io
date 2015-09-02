---
layout: post
title: "Log Aggregation with Tomcat, Log4j, Spring and Logstash"
description: "An example of log aggregation using Tomcat, Log4j, Spring and Logstash"
category: articles
tags: [devops, elasticsearch, java, kibana, log4j, logstash, monitoring, operations, software, Spring, tomcat]
comments: true
---

# 2014-11-28

While parsing log files is a fine way for Logstash to ingest data, there are several other methods to ship the same information to Logstash.  These methods each have trade-offs that may make them more or less suitable for your particular situation.  I have posted about [multiline tomcat log parsing]({% post_url 2014-01-12-logstash-multiline-tomcat-log-parsing %}) before, but this post is an attempt to compare the other methods I've explored.

_Just a note before I dive in - I'm using Java 7, Spring 4, Logstash 1.4.2 and Elasticsearch 4.1._

## Log4j over TCP
This method uses Logstash's [log4j](http://logstash.net/docs/1.4.2/inputs/log4j) input and log4j's
