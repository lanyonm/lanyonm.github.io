---
layout: post
title: "MyBatis Spring Java Config Contribution"
description: "Contributing to the creation of first-class support for Java Config in MyBatis-Spring"
category: articles
tags: [development, java, MyBatis, Spring, software]
comments: true
---

![MyBatis Spring](http://mybatis.github.io/images/mybatis-logo.png)

As you may have guessed from a [previous post]({% post_url 2013-01-06-spring-grabbag %}), I prefer Java Config.  At times in the past I've been forced to go with what's currently supported instead of spending the time necessary to add the feature I'd like to have.  With the Spring Grabbag project, I have that time.

The current mybatis-spring project (v1.1.1) only has support for XML-defined config.  Some searching lead me to java/xml config hybrids, like the one described [here](https://groups.google.com/forum/#!msg/mybatis-user/J4D6FeUBGZA/dPdFcbWQ4VUJ), but that seemed too much like the compromise I'd been forced to make in the past.  Some more targeted searching lead me to [this issue](https://code.google.com/p/mybatis/issues/detail?id=694) on the MyBatis issue tracker, which in turn lead me to a [more technically robust ticket](https://jira.springsource.org/browse/SPR-9464?focusedCommentId=79600&page=com.atlassian.jira.plugin.system.issuetabpanels:comment-tabpanel#comment-79600) on SpringSource's Jira instance.

At this point I knew:

* there was no code yet-written to satisfy my predicament
* that the SpringSource folks expected the MyBatis-Spring code to follow the established ``@Enable`` pattern
* that Chris Beams had very graciously [written code](https://github.com/SpringSource/spring-framework-issues/commit/a1584d7aa1906ab06ffe0dc8161c187647c8f6cc) that reproduced the situation and committed it to the spring-framework-issues repo

Now all I had to do was learn the Spring bean lifecycle and write the solution.  While the [documentation](http://static.springsource.org/spring/docs/3.2.x/spring-framework-reference/html/beans.html#beans-factory-extension) is great, it's also a bit dense.  I chose to read up on [EnableWebMvc](https://github.com/SpringSource/spring-framework/blob/3.2.x/spring-webmvc/src/main/java/org/springframework/web/servlet/config/annotation/EnableWebMvc.java), [ComponentScanAnnotationParser](https://github.com/SpringSource/spring-framework/blob/3.2.x/spring-context/src/main/java/org/springframework/context/annotation/ComponentScanAnnotationParser.java), [AspectJAutoProxyRegistrar](https://github.com/SpringSource/spring-framework/blob/3.2.x/spring-context/src/main/java/org/springframework/context/annotation/AspectJAutoProxyRegistrar.java), and [BatchConfigurationSelector](https://github.com/SpringSource/spring-batch/blob/master/spring-batch-core/src/main/java/org/springframework/batch/core/configuration/annotation/BatchConfigurationSelector.java) and more specifically how configurers, adapters and registrars are used in the context of Spring annotations.  Given that the MapperScanner is registering new beans to the application context, [adding a registrar](https://github.com/LanyonM/mybatis-spring/commit/9972cdba5538acf3ac527b446bd73dd450afabe0) made most sense.  I had been in contact with [Eduardo Macarron](https://github.com/emacarron), the maintainer of the MyBatis-Spring project, and he altered the code as necessary to be accepted into the code base.

It feels good to be able to @MapperScan my DataConfig and have it work like you'd hope and expect.  It feels great to meaningfully contribute back to a project I've relied on so much in the past.
