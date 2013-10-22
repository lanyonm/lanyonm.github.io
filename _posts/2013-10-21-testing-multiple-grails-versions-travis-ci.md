---
layout: post
title: "Testing With Multiple Grails Versions on Travis-CI"
description: "How to test a Grails project on Travis-CI with multiple versions of Grails"
category: articles
tags: [grails, testing, travis-ci]
og:
  image: 'http://about.travis-ci.org/images/travis-mascot-200px.png'
  type: 'image/png'
  width: '201'
  height: '199'
comments: true
---

Maintaining plugins for quickly evolving frameworks can become burdensome if the testing tools don't help you ensure backward compatibility.  We have been slowly incorporating better testing into the [Grails Feature Toggle Plugin](https://github.com/LanyonM/grails-feature-toggle) and have been looking to test all minor versions of Grails 2.  If only there were a way for Travis-CI to test all those versions of Grails…

<div class="center grails-travis">
  <img src="http://about.travis-ci.org/images/travis-mascot-200px.png" alt="Travis-CI" />
  <span>+</span>
  <img src="http://solutions4all.info/img/image/grails-manual-insert-query.png" alt="Grails" />
</div>

Thanks to [bjfish](https://gist.github.com/bjfish), there's a quick and easy way to have Travis test multiple versions of Grails.  Using GVM, you can install an environment-specified version of Grails within Travis.  We have successfully integrated this approach into the Feature Toggle Plugin.  Have a look at our `.travis.yml` here:

{% highlight yaml linenos %}
language: groovy

jdk:
- oraclejdk6

env:
- GRAILS_VERSION=2.3.1
- GRAILS_VERSION=2.2.4
- GRAILS_VERSION=2.1.5
- GRAILS_VERSION=2.0.4

before_install:
- rm -rf ~/.gvm
- curl -s get.gvmtool.net > ~/install_gvm.sh
- chmod 775 ~/install_gvm.sh
- ~/install_gvm.sh
- echo "gvm_auto_answer=true" > ~/.gvm/etc/config
- source ~/.gvm/bin/gvm-init.sh
- gvm install grails $GRAILS_VERSION || true

branches:
  only:
    - master
    - more-testing

script: grails clean
     && grails upgrade --non-interactive
     && grails test-app --non-interactive
{% endhighlight %}

Another likely influential [post](http://www.christianoestreich.com/2013/05/travis-ci-grails-gvm/) outlines this same approach and the comments ([this one in particular](http://www.christianoestreich.com/2013/05/travis-ci-grails-gvm/#comment-992555180)) discuss whether this is the cleanest solution.  It certainly sounds like something to look into.

Hopefully using Travis-CI to test multiple versions of Grails will help maintainers establish backward compatibility for their plugins and libraries.
