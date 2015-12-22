---
layout: post
title: "Publishing a Maven Site to GitHub Pages with Travis-CI"
description: "How to publish a Maven site to GitHub Pages with Travis-CI"
category: articles
tags: [devops, documentation, github, java, maven, software, travis-ci]
comments: true
---

Part of continuous delivery is continuously delivering documentation along with the software. I'd go so far as to argue that it's _part of_ the software. In the past I've had to remember to run `mvn site` periodically to ensure that the latest [javadoc](http://blog.lanyonm.org/playground/apidocs/index.html) and [dependency updates report](http://blog.lanyonm.org/playground/dependency-updates-report.html) get created, but _there's gotta be a better way!_

The key to this integration is having Travis authenticate back to GitHub to publish to gh-pages in a secure way. The default suggestion for publishing with GitHub's [site-maven-plugin](https://github.com/github/maven-plugins) is to add your username & password or an oauth token to `~/.m2/settings.xml`. This won't work for Travis-CI and would leak the oauth token.

## POM Configuration
The site-maven-plugin configuration is exactly the same as [GitHub's example](https://github.com/github/maven-plugins#example), but that's to be expected. The important configuration is to allow the oauth token to be read from an environment variable (excerpt from [`pom.xml`](https://github.com/lanyonm/playground/blob/85543d301e0955e3f6031053fe720888df58c53c/pom.xml)):

{% highlight xml %}
<project>
    <properties>
        <github.global.server>github</github.global.server>
        <github.global.oauth2Token>${env.GITHUB_OAUTH_TOKEN}</github.global.oauth2Token>
    </properties>
</project>
{% endhighlight %}

To be able to run `mvn site` locally you'll need to run `export GITHUB_OAUTH_TOKEN="your-github-personal-access-token"` or add that line to your dotfiles. To create the token follow these [instructions](https://help.github.com/articles/creating-an-access-token-for-command-line-use/). The token I created has repo and user:email access.

## Travis Encrypted Environment Variable
Getting your GitHub token into the Travis-CI environment var is [very well documented](https://docs.travis-ci.com/user/environment-variables/#Encrypted-Variables). Here's a handy copy/paste of the command you'll want to run to encrypt your environment variable:

{% highlight bash %}
travis encrypt GITHUB_OAUTH_TOKEN="your-github-personal-access-token" --add env.global
{% endhighlight %}

The one thing not covered in the Travis-CI docs page is that you can have multiple encrypted environment variables like so:

{% highlight yaml %}
env:
  global:
    secure: bigEncryptedString/One
    secure: bigEncryptedString/Two
{% endhighlight %}

## Summary
You can see this working in my Spring [playground](https://github.com/lanyonm/playground) repository which publishes [here](http://blog.lanyonm.org/playground/). Please let me know if you find this helpful or have suggestions for improvements.
