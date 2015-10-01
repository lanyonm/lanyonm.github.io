---
layout: post
title: "ChatOps: Hubot Grafana Images in HipChat"
description: "Golang app to save grafana-rendered images, shorten the url, and serve from a local webserver"
category: articles
tags: [chatops, chef, data visualization, devops, golang, grafana, monitoring, nginx, operations, ruby, sensu, software]
comments: true
---

As we continue toward ChatOps and making our work visible at work, the next phase of maturing our monitoring systems is to create a query-able interface to our visualization system (Grafana) from HipChat. Grafana is a system I've become quite fond of and helped author the Chef cookbook for. The HTTP API for Grafana has matured, and the time seemed right to create this integration.

## High-level Design
Having read about [Librato's ChatOps](http://blog.librato.com/posts/confessions-of-a-chatbot) and seen [Etsy's nagios-herald](https://github.com/etsy/nagios-herald), I had a rough idea of the user experience I wanted. With a head full of hindsight bias, here are some of the requirements:

* A user-friendly query interface in chat (no magic numbers, server-specific names, etc.)
* Images posted should be available in chat without additional authentication
* Able to utilize our existing Grafana server

I was delighted to find that Stephen Yeargin had already written [hubot-grafana](https://github.com/stephenyeargin/hubot-grafana), a script that did all the heavy lifting for the first requirement. His hubot script provides for discovery of dashboards, per-panel queries, template variables, and time-range queries. It's really quite fantastic. However, it assumes that S3 will be used to host the images. While that'll work for most folks (and certainly could work for us), I wanted to be able to use our existing Grafana server to house this integration. To achieve this I had to modify [grafana.coffee](https://github.com/criticalmass/hubot-grafana/blob/master/src/grafana.coffee). More on that below.

The default configuration provided by the [chef-grafana](https://github.com/JonathanTron/chef-grafana) cookbook includes Nginx as a proxy for grafana-server. For work we wrap the community cookbook to configure TLS, LDAP, and Grafana's datasources. It seemed like a natural extension of visualization's responsibility to have a small app on the Grafana node that can fetch/save rendered panel images and then use Nginx to serve those images. I called that small application [grafana-images](https://github.com/lanyonm/grafana-images). More on that below as well.

## Modifications to hubot-grafana
As mentioned above, I had to modify the [hubot-grafana](https://github.com/criticalmass/hubot-grafana) script to provide an alternate image persistence method (alternative to S3). The coffeescript additions are relatively straightforward:

{% highlight coffeescript %}
customFetchAndUpload = (msg, title, url, link) ->
  requestHeaders = {
    encoding: "utf8",
    Authorization: "Bearer #{grafana_api_key}",
    Accept: "application/json"
  }

  req_opts = {
    method: "POST",
    url: "#{grafana_images_host}/grafana-images",
    headers: requestHeaders,
    json: {
      imageUrl: url
    }
  }

  # post to grafana-images
  request req_opts, (err, res, json) ->
    robot.logger.debug "grafana-images POST: #{req_opts.url}, content-type[#{res.headers['content-type']}]"

    if res.statusCode == 200
      sendRobotResponse msg, title, json.pubImg, link
    else
      robot.logger.debug res
      robot.logger.error "Upload Error Code: #{res.statusCode}"
      msg.send "#{title} - [Access Error] - #{link}"
{% endhighlight %}

The Grafana API key is provided to the script by an environment variable and the newly added environment variable `HUBOT_USE_GRAFANA_IMAGES` determines whether or not to use the `customFetchAndUpload` code-path. The full diff can be found [here](https://github.com/criticalmass/hubot-grafana/commit/a802a816b21f61b1cf4d61f0f4967fcd97fb9bf8#diff-8387f8787e3a34b1530cc6f1a1ff23e2).

As you can see, the `/grafana-images` uri is hard-coded. That's because the route used by `grafana-images` is hard-coded. Also, note that the necessary authentication token is passed along with the json payload. In many ways this function is treating `grafana-images` as a proxy for Grafana.

Another addition to note is the help text I added to the hubot script. You can ask the bot "`graf help`" and it'll respond with increasingly complex query samples. Yay for user friendliness!

## grafana-images
Following my experience with [http-stats-collector]({% post_url 2015-03-29-golang-http-stats-collector %}), Golang seemed like a good choice for the small application. It acts as a proxy and therefore expects only two things: a valid API token and json payload containing the full Grafana panel render url. To give more context to what's happening, here's an http call diagram:

<div class="center">
  <figure>
    <a href="{{ site.url }}/images/grafana-images-diagram.svg"><img src="{{ site.url }}/images/grafana-images-diagram.svg" /></a>
    <figcaption>The http calls required for hubot-grafana using grafana-images numbered by sequence</figcaption>
  </figure>
</div>

The `customFetchAndUpload` function described above is call #4. From there `grafana-images` will fetch (#5 & #6), save, and return a sharable image url via json (#7). Here's a snippet from `grafana-images`' [handlers.go](https://github.com/lanyonm/grafana-images/blob/master/handlers.go):

{% highlight go %}
// Fetch image
var client = http.Client{}
req, err := http.NewRequest("GET", image.Url, nil)
req.Header.Add("Accept", "application/json")
req.Header.Add("Authorization", token)
resp, err := client.Do(req)
if err != nil {
  log.Fatalf("http.Get -> %v", err)
  w.WriteHeader(500)
  return
}
data, err := ioutil.ReadAll(resp.Body)
if err != nil {
  log.Fatalf("ioutil.ReadAll -> %v", err)
  w.WriteHeader(500)
  return
}

// Save image
fileName := fmt.Sprintf("%x.png", md5.Sum(data))
resp.Body.Close()
err = ioutil.WriteFile(fmt.Sprintf("%s/%s", imagePath, fileName), data, 0666)
if err != nil {
  log.Fatalf("ioutil.WriteFile -> %v", err)
  w.WriteHeader(500)
  return
}

// Return image location
w.Header().Set("Content-Type", "application/json")
fmt.Fprintf(w, "{\"pubImg\":\"%s/%s\"}", imageHost, fileName)
{% endhighlight %}

There are several variables assumed to be set:

* `image` - the requested `imageUrl` from the json
* `token` - the contents of the `Authorization` header
* `imagePath` - a path on disk to store the saved images
* `imageHost` - the host used in the building the json response

If everything is configured correctly, the Grafana dashboard panel will be saved to disk and the json sent back to `hubot-grafana`. Further detail can be found [on GitHub](https://github.com/lanyonm/grafana-images). I tired to make all the error messages helpful and actionable, but if you find an error condition that isn't well explained, please open a GitHub issue.

### Security
You may have noticed that the app very simply downloads whatever is specified at `imageUrl` and saves it as a png. This can be dangerous given that nothing checks to ensure that the contents are in-fact an image and not an exploit. _Take care_ to only allow specific traffic to make requests of `grafana-images`. I may add a check via Golang's png package to ensure proper encoding, but it may be quite some time before that happens (pull requests welcome).

## Nginx Config
As mentioned above, I used Nginx to proxy grafana-server. I also use it to proxy `grafana-images` and serve the saved panel images. Here's a sample conf that should would for this purpose:

{% highlight nginx %}
# the grafana-server config has been omitted
upstream grafana-images {
  server 127.0.0.1:8080;
}

server {
  # excerpt for grafana-images
  location /grafana-images {
    proxy_pass http://grafana-images;
    allow 10.0.0.11; # ip of server running hubot
    deny all;
  }
  location /saved-images {
    root /opt;
  }
}
{% endhighlight %}

Note that the `imageHost` passed to `grafana-images` is the FQDN _plus_ the location of the saved images. The value used will be dependent on the web server hosting the saved images.

## Other Uses
Because `grafana-images` exposes its functionality over a simple HTTP API, expanding its purpose should be straightforward. The app expects an `"Authorization: Bearer grafana-token-goes-here"` header and a json payload:

{% highlight json %}
{
  "imageUrl": "https://grafana.example.com/render/dashboard-solo/db/sample-dashboard/?panelId=5&width=1000&height=500&from=now-6h&to=now&var-server=test-server"
}
{% endhighlight %}

### Sensu Notifications
At work we have incorporated Grafana panel image embedding functionality into our Sensu HipChat handler. We started with the [Sensu community HipChat handler](https://raw.githubusercontent.com/sensu/sensu-community-plugins/e2286b69eda081b4c59226667245e95f4c3a45e1/handlers/notification/hipchat.rb) and modified the message body heavily for our purposes.

The code to add Grafana panel images to Sensu HipChat notifications is roughly:

{% highlight ruby %}
if @event['check']['graph_image']
  # do some work to get the static image from grafana-images
  uri = URI.parse('https://grafana.example.com/grafana-images')
  http = Net::HTTP.new(uri.host, uri.port)
  http.use_ssl = true
  request = Net::HTTP::Post.new('/grafana-images')
  request.add_field('Content-Type', 'application/json;charset=utf-8')
  request.add_field('Authorization', 'Bearer grafana-token-goes-here')
  request.body = { 'imageUrl' => "#{@event['check']['graph_image']}&from=now-6h&to=now" }.to_json

  begin
    response = http.request(request)
    public_image = JSON.parse(response.body)['pubImg']
    message << "<br /><a href=\"#{public_image}\"><img src=\"#{public_image}\" /></a><br />"
  rescue StandardError => e
    message << " - [graph_image fetch failed (#{e})]"
  end
end
{% endhighlight %}

The `@event['check']['graph_image']` value is assumed to be a valid dashboard panel render url _without_ the from/to times: `https://grafana.example.com/render/dashboard-solo/db/sample-dashboard/?panelId=5&var-server=test-server&width=1000&height=500`. The `panelId` is can be obtained from the UI of the dashboard.

We manage our infrastructure with Chef and it creates all the Sensu checks, thus allowing us to programmatically build the checks. We add a `graph_image` attribute to the check that contains a panel render url associated with the metric(s) that can help provide context to the Sensu notification. Chef can give the FQDN of the Grafana node as well as the values for template attributes, so it all comes together quite cleanly.

## Other Considerations
One thing not handled by `grafana-images` is saved image retention. You'll need to create a purge policy that works for you. Once I've figured out how we're going to handle that, I'll add it here. :)
