---
layout: post
title: "Web Performance Monitoring - DevOpsDays MSP 2015"
description: "Give your teams the tools to form a relationship with prod"
category: speaking
tags: [culture, data visualization, devops, devopsdays, elasticsearch, front-end, golang, kibana, logstash, monitoring, operations, webperf]
og:
  image: 'dod-msp-lanyonm-ignite.jpg'
  type: 'image/jpg'
  width: '600'
  height: '450'
comments: true
---

I initially intended to speak about how we use configuration management to automate our real user measurement (RUM), but as I was putting together my talk I discovered that the real insight was how the same tools can be used to facilitate the front-end developer's relationship with prod.

I opened the Ignite by speaking about the lack of operational visibility into the end user's experience and how our initial attempt to close this gap was to use the Navigation Timing data. We use a Golang program called [http-stats-collector]({% post_url 2015-03-29-golang-http-stats-collector %}) to collect NavTiming data as well as javascript errors and CSP reports. Looking at the data after it was processed by our monitoring pipeline, we saw that the real insight was how javascript errors could tell the story of the end user's experience - something NavTiming data did not do for us.

I concluded the talk with a sampling of the systems and templates we have in place to facilitate the collection of data. While this understanding of the end user experience is valuable, the data collection and visualization needs to be turn-key for it to be used across our organization.

<https://speakerdeck.com/lanyonm/web-performance-monitoring>

<script async class="speakerdeck-embed" data-id="932c1c5a6d2c4ed899a19893908bb64f" data-ratio="1.77777777777778" src="https://speakerdeck.com/assets/embed.js"></script>

<https://youtu.be/ku3O4HnMXrM?t=395>

<div class='embed-container'><iframe src='http://www.youtube.com/embed/ku3O4HnMXrM?t=400' frameborder='0' allowfullscreen></iframe></div>

_All photo credits including those in the `og:metadata` go to [Bridget Kromhout](https://twitter.com/bridgetkromhout) or DevOpsDays Minneapolis 2015._

Here's a transcript of the talk:

1. Hi, my name is Mike Lanyon, and I work at a digital ad agency called Critical Mass. I would like to talk about web performance monitoring. In DevOps we often talk about monitoring of the systems that provide experiences, but not the monitoring of the end user's experience itself.
2. Critical Mass is a digital experience design agency. That means that we put the customer at the center of our process, through strategy, design, technology and analytics. We want to use our influence with clients to make their customers' lives better.
3. More specifically than web performance, I'd like to talk about a front end developer's relationship to prod. In years past this relationship may have been through an FTP client, but no-matter the technology there was a gap in operational visibility.
4. The front-end developer's preparation for production has gotten quite robust. Run sass, concat & minify js. Maybe there's a CDN, but then it gets a bit fuzzier... Where is the operational visibility in this?
5. WebPage test is a tool our teams use to quantify the end user's experience. This chart shows the composite Speed Index of one of our web pages. The Index is the integral of the space above the charted lines, which represent the perceived completion of the page load.
6. But still there is no operational visibility. There's no way for a web developer on my team to understand the performance of a user currently visiting our site. There's nothing analogous to the app log with a stack trace detailing the user's crummy experience.
7. RUM - real user monitoring. This is something that began to pop up a few years ago. This is different than synthetic monitoring because you're collecting data from the experience of _real_ users.
8. Navigation Timing API is one of the most well established means to collecting the real user's performance. There are several solutions that will capture this information for you like Google analytics or NewRelic.
9. Golang. I toyed around with Go a couple years ago, and didn't really understand how it could be useful to me at the time - but it's reputation for being fast seemed like a good fit for collecting RUM performance data.
10. I created https-stats-collector. Inspired by a GDSTeam project called event-store that saves content security policy reports. I don't really want to focus much on the Golang code here - only to highlight that it's open source and would love to have some feedback on the project.
11. There are three primary routes offered by the application: nav-timing, js-error, and csp-report. In addition to nav-timing, I'll talk about js-errors, which is fed by a global javascript error and logs the errors experienced by users.
12. As you can see, after nav-timing data is processed by our monitoring pipeline we're able to create pretty, squiggly line graphs. I really enjoy these, and I think they're great, but they don't help tell the end user's story.
13. This is screencap of Kibana showing the errors captured by the js-errors handler and processed by our ELK stack. When one of the senior developers first saw this, he pointed to a cluster of errors experienced by a single user and said, "I wonder what the story is there".
14. We have found that while nav-timing data is really cool, javascript error reporting is the game changer. It gave the teams a level of traceability they'd never had before and equated to a front-end version of the app log.
15. This capability is really valuable, but it has to be operationalized and become part of the default path or path of least resistance.
16. We use Chef to put all the bits in place, http-stats-collector, statsd, logstash, elasticsearch, influxdb, kibana, grafana, etc. Configuration management also helps us standardize and scale the implementation.
17. Sample implementations that are framework agnostic help the client/product teams adopt the pattern and integrate it into their work.
18. We have gone so far as to make these RUM collection tools part of our standard stack. In this example a team asked for a simple webserver, and they got the webserver - but packed with all the data collection bits pre-installed.
19. If you take anything from this talk, please consider how to help create the connection between your technology teams and your users. Give your teams the tools to make this connection with prod - to form this relationship with the individual end user.
20. Thank you
