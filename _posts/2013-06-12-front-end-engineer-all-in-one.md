---
layout: post
title: "Front-End Optimization, Monitoring & Deployment Engineer All-In-One"
description: "A more broadly encompassing look at the responsibilities of a front-end developer"
category: articles
tags: [development, front-end, software, operations]
comments: true
---

# TL;DR
Why doesn't front-end ops need to be a separate role?  Because the developers building your pages know those pages best, know what tooling is needed and should be thinking about how those pages perform.  How do you get those folks interested in and caring about performance and ops?  Well, good luck with the ops part, but to get developers to espouse performance, create fast-feedback loops that allow performance data to be visualized.  That visualization is the enzyme that allows digestion of data.  Once you have that feedback loop established, keep the data fresh and the atmosphere enthusiastic.

# The Back-story
A recent [article](http://www.smashingmagazine.com/2013/06/11/front-end-ops/) in Smashing Magazine struck a cord with me.  It was about front-end ops and how it should be a distinct role from front-end development.  It was refreshing to see an enumeration of these tasks.  I come from the development side and am passionately interested in operations and doing all the things that make us happy doing what we do and that makes our products better.

As the person primarily responsible for our deployment pipeline at work, I have worked with the team to assure the deploy process takes care of everything from minification, concatenation, and running Compass to the automated functional testing grid, deploying wars, and flushing/warming caches.  These are parts of continuous integration that once configured, should fade into the background.  None of these activities should be manually triggered or require developer input on a regular basis.

After we had all that in place, we turned our sights to monitoring.  Monitoring RUM data time-series style is also something that fades into the background after it's been established.  I try to elicit the competitive spirit by making sure performance data is always visible on a dashboard in a highly foot trafficked area.  Using tools like WebPageTest.org allow you to see a filmstrip of page load progress snapshots.  Once you've seen snapshots at 100ms intervals of a page loading, you wonder exactly how your primary pages look at that speed.

Error logging can be gamified in a similar way.  A dashboard can playfully display the time between errors either in raw numbers or with animations - essentially showing a happy website or product when times are good.

Rather than making this a distinct role, I would argue that it is leadership's responsibility to make time for these activities and, more importantly, to make sure a sense of purpose, imperative and fun is felt for these tasks.  While premature optimization is a bad thing, a well rounded developer will consider performance ramifications when laying out a page.  Essentially the developer will build performance _into_ the page, much the same way quality can be built into a process.
