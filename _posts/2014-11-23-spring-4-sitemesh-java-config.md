---
layout: post
title: "Spring 4 and SiteMesh with Java Config"
description: "An example of SiteMesh 2.4.2 integration with Spring 4 using Java Config"
category: articles
tags: [development, java, SiteMesh, software, Spring]
comments: true
---

If you're creating a web application with Spring MVC you'll want to use a view-layer framework.  I've used Grails for several projects at work, and the decorator pattern applied to view-layer files has been a nice way to approach the view-layer architecture.  Grails uses [SiteMesh](http://wiki.sitemesh.org/wiki/display/sitemesh/Home) under the hood, so I wanted to understand how SiteMesh comes together with Spring.

***Please note***: The examples for this post use Spring 4.0.6 and SiteMesh 2.4.2. A new major version of SiteMesh has been released but has not been tested with the suggestions in this post.

## Configuration
If you've seen any of my other posts, you'll know that I like [Java]({% post_url 2014-04-21-spring-4-mybatis-java-config %}) [Config]({% post_url 2013-01-19-mybatis-spring-java-config-contribution %}) for Spring. The first place SiteMesh is added to Spring MVC in a Java Config project is in the dispatcher servlet filter chains, which takes us to the [`AppInitializer`](https://github.com/lanyonm/playground/blob/1e64796125afd93aa1f69f763c91c8dea7aaa935/src/main/java/org/lanyonm/playground/config/AppInitializer.java):

{% highlight java %}
public class AppInitializer extends AbstractAnnotationConfigDispatcherServletInitializer {

    ...

    @Override
    protected Filter[] getServletFilters() {
        CharacterEncodingFilter characterEncodingFilter = new CharacterEncodingFilter();
        characterEncodingFilter.setEncoding("UTF-8");
        return new Filter[]{ characterEncodingFilter, new SiteMeshFilter() };
    }
}
{% endhighlight %}

I'm extending [AbstractAnnotationConfigDispatcherServletInitializer](http://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/web/servlet/support/AbstractAnnotationConfigDispatcherServletInitializer.html), which gives the ability to provide a list of list of `Filter`s via [`getServletFilters`](http://docs.spring.io/spring/docs/current/javadoc-api/org/springframework/web/servlet/support/AbstractDispatcherServletInitializer.html#getServletFilters--).  You can see that I chose to specify a charset filter in addition to the SiteMesh filter.

The second piece of configuration is an xml file that tells SiteMesh where to look for templates and how they apply to view-layer files (like jsps).  Here's the [`decorators.xml`](https://github.com/lanyonm/playground/blob/1e64796125afd93aa1f69f763c91c8dea7aaa935/src/main/webapp/WEB-INF/decorators.xml):

{% highlight xml linenos %}
<?xml version="1.0" encoding="UTF-8"?>
<decorators defaultdir="/WEB-INF/decorators/">
    <excludes>
        <pattern>/users</pattern>
    </excludes>
    <decorator name="default" page="default.jsp">
        <pattern>*</pattern>
    </decorator>
</decorators>
{% endhighlight %}

The configuration on line 2 shows that all decorator files are in the `WEB-INF/decorators` folder.  Given that I have [overridden](https://github.com/lanyonm/playground/blob/1e64796125afd93aa1f69f763c91c8dea7aaa935/src/main/java/org/lanyonm/playground/config/ViewResolver.java) Spring's view resolver to look for view files in `WEB-INF/views`, this makes sense.  In lines 3-5 I ignore the `/users` uri pattern, and on lines 6-8 I setup a decorator.

## Usage
Going forward, I'll be using the term template and decorator interchangeably, and as you'll see below, the term template is quite applicable.  I'm using Bootstrap for the UI of the playground demo, so there's quite a bit of boilerplate code required on each page.  Using the default template I can ensure each page gets exactly the same header, navigation and footer.

### SiteMesh Tags
There are a couple important SiteMesh tags to understanding how the index page gets decorated with `default.jsp`.  The default decorator reads like the shell of an html page:

{% highlight html linenos %}
<%@ taglib prefix="dec" uri="http://www.opensymphony.com/sitemesh/decorator" %>
<!doctype html>
<html class="no-js" lang="en">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <title><dec:title default="playground" /></title>

    global css goes here...

    <dec:head />
</head>
<body>
    <div class="container">
        <dec:body />
    </div>

     global javascript goes here...

</body>
{% endhighlight %}

Here are the important SiteMesh tags used above:

* `<dec:title default="..." />` - This sets a default title for all pages decorated by this template.  If you specify a `<title>` tag in the head of a view-layer file, it will replace the value set here.
* `<dec:head />` - This is where page-specific `<head>` elements are added to the head elements provided in the template.  It is important to remember that what's in the individual page is _added_ to the `<head>` of the template.
* `<dec:body />` - This tag is where the `<body>` content of the view-layer file will be inserted into the template.  All of the elements within the `<body>` of the individual page will be added, so it is important to carefully reason about the nesting of content within the template.

There's not a single great example of how these tags are used within SiteMesh, but there's a decent [10-minute starter guide](http://wiki.sitemesh.org/wiki/display/sitemesh/SiteMesh+Adept+in+10+Minutes).  In addition to the SiteMesh tags, another implementation detail to keep in mind is that that jstl tags are limited to the context of the file in which they are included.  You cannot stack all your jstl declarations at the top of the template and have them accessible to the individual page as it renders.

## Conclusion
There are other, more fully featured view-layer frameworks, but for my taste the SiteMesh decorator pattern strikes the right balance.  By no means is this example a comprehensive demonstration of SiteMesh's capability, but it is a starting point and has hopefully peaked your interest.
