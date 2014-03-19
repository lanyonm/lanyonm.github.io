---
layout: post
title: "Alphabetizing Jekyll Page Tags In Pure Liquid (Without Plugins)"
description: "How to Alphabetize Jekyll Page Tags in Pure Liquid - no plugins"
category: articles
tags: [github, jekyll, liquid, ruby]
comments: true
---

When you [host a Jekyll site on GitHub](https://help.github.com/articles/using-jekyll-with-pages), it renders the site in safe-mode.  This means you can't use any plugins enhance Jekyll's functionality and, more specifically, you can't write a [Liquid tag](https://github.com/Shopify/liquid/wiki/Liquid-for-Programmers#create-your-own-tags) that alphabetizes the site's tags.  Unordered tags make a Jekyll tag list look sloppy, so if you care about the details, you likely want your tag list to be alphabetized.

It's easy to alphabetize the tag list on a given page (just list the tags alphabetically), but getting your [`tags.html`](/tags.html) to list tags alphabetically is a bit more convoluted if you aren't able to use plugins.

# Waist-Deep in Liquid
Liquid provides some pretty good [documentation](http://docs.shopify.com/themes/liquid-basics/logic) for figuring out what logical operators and functions are built into the templating language.  Particularly useful are `capture` and `assign`, which each capture values as variables.  These logical operators can contain additional logic like for-loops, splits, sorts and joins.  Here's the code I use to generate a sorted list of tags:

{% highlight html linenos %}{% raw %}
{% capture site_tags %}{% for tag in site.tags %}{{ tag | first }}{% unless forloop.last %},{% endunless %}{% endfor %}{% endcapture %}
{% assign tag_words = site_tags | split:',' | sort %}
{% endraw %}{% endhighlight %}

Line 1 above will get the tag name for every tag on the site and set them to the `site_tags` variable.  Each tag object contains both the tag name and a list of the associated posts.  This capture statement is all on one line so that the commas can reliably be used as delimiters.  Line 2 creates the `tag_words` variable that is a sorted array of the tag names.  If you want to see what these two statements would produce within Jekyll, you'll find them printed in html comments on my [tags page](/tags.html).

# Building The HTML
As you can see on [`tags.html`](/tags.html), the tags are listed alphabetically with post counts and then each tag's post is listed below.  Here's the Liquid code:

{% highlight html linenos %}{% raw %}
<div id="tags">
  <h1>Tags</h1>
  <ul class="tag-box inline">
  {% for item in (0..site.tags.size) %}{% unless forloop.last %}
    {% capture this_word %}{{ tag_words[item] | strip_newlines }}{% endcapture %}
    <li><a href="#{{ this_word | cgi_escape }}">{{ this_word }} <span>{{ site.tags[this_word].size }}</span></a></li>
  {% endunless %}{% endfor %}
  </ul>

  {% for item in (0..site.tags.size) %}{% unless forloop.last %}
    {% capture this_word %}{{ tag_words[item] | strip_newlines }}{% endcapture %}
  <h2 id="{{ this_word | cgi_escape }}">{{ this_word }}</h2>
  <ul class="posts">
    {% for post in site.tags[this_word] %}{% if post.title != null %}
    <li itemscope><span class="entry-date"><time datetime="{{ post.date | date_to_xmlschema }}" itemprop="datePublished">{{ post.date | date: "%B %d, %Y" }}</time></span> &raquo; <a href="{{ post.url }}">{{ post.title }}</a></li>
    {% endif %}{% endfor %}
  </ul>
  {% endunless %}{% endfor %}
</div>
{% endraw %}{% endhighlight %}

On line 4 you'll notice an `unless forloop.last`.  This is because it's a quick an easy way to keep the array index in bounds.  Lines 6 and 14 show how you can use a tag's name to pull the tag from `site.tags`.  I checked for `post.title != null` because I don't want to display pages without titles.

# TL;DR
Alphabetizing Jekyll site tags is trickier than it should be.  If you plan to deploy the site via GitHub Pages, you can't use plugins.  The [source code](https://github.com/LanyonM/lanyonm.github.io/blob/master/tags.html) for my pure-Liquid, alphabetized tags is on GitHub and deployed [here](/tags.html).
