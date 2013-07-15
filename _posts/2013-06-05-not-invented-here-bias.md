---
layout: post
title: "Not Invented Here Bias"
description: "Biases are often subconscious and can present dangerous deviations in our judgment"
category: articles
tags: [culture, software, theory]
comments: true
---

# Biases In Software
Earlier this week I read a [post](http://www.jonathanklein.net/2013/06/cognitive-biases-in-software-engineering.html) by Jonathen Klein about cognitive biases in software engineering.  I posted it on work's internal wiki and my peers quickly added other biases that they see in their day-to-day.  As a recap, here are the biases from Jonathan's post:

* _Fundamental Attribution Error_ - overestimate the effect of personality and underestimate the effect of circumstance
* _Confirmation Bias_ - prefer information that supports personal beliefs
* _Bandwagon Effect_ - the probability of any individual adopting a trend grows with the trend's popularity
* _Hyperbolic Discounting_ - people prefer to receive less now than more later
* _Negativity Bias_ - the psychological phenomenon where humans give more credence to the negative than the positive

I don't have much to say that hasn't already been said about these.  Jonathan's post is pretty awesome as were [others](http://www.kitchensoap.com/2012/10/25/on-being-a-senior-engineer/) [before](http://www.amazon.com/Thinking-Fast-Slow-Daniel-Kahneman/dp/0374533555).

# Not Invented Here Bias
The comments on our internal wiki could be summarized as _Roll Your Own_ or _Not Invented Here_ bias.  Examples were building customized messaging and queuing when JMS would have worked, or building a web-tier cache when Varnish would have been perfect.  I am assuming that, as engineers, we strive to use existing, proven situations instead of creating new solutions.  The Not Invented Here bias can be the result of a handful of circumstances:

* The perception that the current challenge is unique and therefore requires a unique solution
* External solutions are insufficient or too complex to apply to the challenge
* A poor incentive structure that compensates time & materials instead of providing value to the customer

I have often seen hand-rolled Java implementations that certainly don't require Spring tooling, but later on needed transaction management, a scheduler, better MVC definition, service layer cache, etc.  Starting with a framework and/or boilerplate would arguably would make the barrier to entry lower and hopefully give the code better structure and extensibility.  There are too many good component-driven, pluggable frameworks out there to go inventing something new without some serious research.

In a time and materials world, it is often easier to write code than to work with the business to add value.  For example, a website build requires that the business be able to author content and use a workflow to manage publication - and track revisions.  In a time & materials world, this undertaking could be lucrative, but if the engineering team chose a CMS with that functionality, time could be spent ensuring the published articles had good SEO, optimizing the site for webperf, implementing web analytics, etc.  There is a certainly lethargy to doing only what is asked, and I see an analogy between that and the type of lethargy that causes repeatable processes to go un-automated.

I am surprised I haven't been able to find a well documented bias that encompasses Not Invented Here.  It seems to be such an endemic and pervasive problem.  If you know of an existing bias that covers this, please let me know.

# TL;DR
_Not Invented Here_ bias is all about rolling your own when there's no reason to do so.  By no means are the biases mentioned here the only ones that affect us in software engineering.  Reviewing them every so often is a helpful reminder of what is often subconscious.  Please leave comments or suggest other biases.
