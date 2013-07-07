---
layout: post
title: "Cognitive Bias"
description: "Biases are often subconscious and can present dangerous deviations in our judgment"
category: articles
tags: [theory, software]
comments: true
---

# Biases In Software
Earlier this week I read a [post](http://www.jonathanklein.net/2013/06/cognitive-biases-in-software-engineering.html) by Jonathen Klein about cognitive biases in software engineering.  I posted it on work's internal wiki and my peers quickly added other biases that they see in their day-to-day.  As a recap, here are the biases from Jonathan's post:

* _Fundamental Attribution Error_ - overestimate the effect of personality and underestimate the effect of circumstance
* _Confirmation Bias_ - prefer information that supports personal beliefs
* _Bandwagon Effect_ - the probability of any individual adopting a trend grows with the trend's popularity
* _Hyperbolic Discounting_ - people prefer to receive less now than more later
* _Negativity Bias_ - the psychological phenomenon where humans give more credence to the negative than the positive

Fundamental attribution error is certainly the bias that I have encountered most.  When explaining it to others, I make this comparison: when you see someone trip over a rock, you think, "Wow, that person is clumsy.  They tripped over a rock."  When you trip over a rock, you blame that damn rock for getting in your way.  It's the rock's fault.

Negativity bias is something I see quite pervasively in the software industry, especially with the attraction to 'disaster porn' and the focus on postmortems.  Don't get me wrong, I believe conducting non-biased and blameless post postmortems is hugely important to general improvement, but we don't nearly as often talk about the importance of retrospectives and how to more broadly apply the successes.  On a smaller scale, I have seen negativity bias combine with fundamental attribution error to cause large swaths of the organization to label IT folks as stupid due to a few bad, but unrelated and external incidents.  I try to use the negativity as fuel to stay positive and build resiliency into our systems and process.

# Not Invented Here Bias
The comments on our internal wiki could be summarized as _Roll Your Own_ or _Not Invented Here_ bias.  Examples were building customized messaging and queuing when JMS would have worked, or building a web-tier cache when Varnish would have been perfect.  I am assuming that, as engineers, we strive to use existing, proven situations instead of creating new solutions.  The Not Invented Here bias can be the result of a handful of circumstances:

* The perception that the current challenge is unique and therefore requires a unique solution
* External solutions are insufficient or too complex to apply to the challenge
* A poor incentive structure that compensates time & materials instead of providing value to the customer

As a Java developer and the company's resident Spring guy, I often see hand-rolled implementations that certainly don't require Spring tooling, but then need transaction management, a scheduler, better MVC definition, service layer cache, etc.  If a boilerplate was provided, it would make the barrier to entry lower and hopefully encourage developers to use established frameworks.  There are too many good component-driven, pluggable frameworks out there to go inventing something new without some serious research.

Poor incentive structures causing Not Invented Here bias could possibly be outside the scope of the bias, but writing code is often easier than working with the business to add value.  For example, a website build requires that the business be able to author content and use a workflow to manage publication - and track revisions.  In a time & materials world, this undertaking could be lucrative, but if the engineering team chose a CMS with that functionality, time could be spent ensuring the published articles had good SEO, optimizing the site for webperf, implementing web analytics, etc.  As we all know, there is always more that can be done to make a website faster or stronger.  We should spend our time doing those things.

# Observer Bias
Observer bias is something we've run into quite a bit as we have rapidly expanded our monitoring.  This is the effect of noticing something that has not been noticed before and wrongly attributing significance.  It takes discipline to wait a couple days for a new graph to develop some history before digging into it's behavior and forming correlations.

# Conclusion
By no means are these biases the only ones that affect us in software engineering.  Reviewing them every so often is a helpful reminder of what is often subconscious.  Please leave comments or suggest other biases.
