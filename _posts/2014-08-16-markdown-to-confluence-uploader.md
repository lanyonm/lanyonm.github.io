---
layout: post
title: "Markdown to Confluence Converter & Uploader"
description: "A small Ruby script to convert markdown to Confluence storage format and upload it to Confluence - md2confl"
category: articles
tags: [documentation, Confluence, markdown, ruby, software]
comments: true
---

# TL;DR
[md2confl](https://github.com/LanyonM/markdown-to-confluence-uploader) is a simple Ruby script to automate the conversion of markdown files to Confluence storage format and then upload them to a Confluence server. It uses [markdown2confluence](https://github.com/jedi4ever/markdown2confluence) to get the markdown to Confluence wiki format and then [confluence-soap](https://github.com/intridea/confluence-soap) to convert wiki format to storage format and upload to Confluence. It can be integrated into your CI workflow to help keep your Confluence documentation up to date.

# The Trouble with Docs...
Remembering to write documentation can be difficult. Getting others to write it can be even more difficult. I've found that in-the-code documentation is the easiest to remember to write and in-repo markdown is a close second. Since each programming language and framework has its preferred way to synthesize in-code documentation, my focus here is on the more popular markdown format. There are several ways to render markdown as HTML, but what about putting it in a shared place that's pervasively recognized as _the place_ to go for documentation? Unless you're lucky enough to have something like GitHub or GitLab in your organization, the markdown documentation can be hard to discover and hard to read.

In my organization we use Confluence to (sometimes) author and share documentation. Because Confluence is quickly becoming the place we can send someone to learn about one of our products, keeping that documentation fresh is important.

# md2confl
I pieced together [md2confl](https://github.com/LanyonM/markdown-to-confluence-uploader/blob/master/md2confl.rb) to automate the conversion and upload of markdown files to Confluence. It uses [markdown2confluence](https://github.com/jedi4ever/markdown2confluence) to get the markdown to Confluence wiki format and then [confluence-soap](https://github.com/intridea/confluence-soap) to convert wiki format to storage format and upload to Confluence. Here's a look at the usage info:

    Usage: md2confl.rb [options...] -s <SPACE_NAME> -i <PAGE_ID>
    assumes defaults that can be set in options parsing...
        -i, --pageId PAGE_ID             REQUIRED. The Confluence page id to upload the converted markdown to.
        -s, --space SPACE_NAME           REQUIRED. The Confluence space name in which the page resides.
        -f, --markdownFile FILE          Path to the Markdown file to convert and upload. Defaults to 'README.md'
        -c, --server CONFLUENCE_SERVER   The Confluence server to upload to. Defaults to 'http://confluence.example.com'
        -u, --user USER                  The Confluence user. Can also be specified by the 'CONFLUENCE_USER' environment variable.
        -p, --password PASSWORD          The Confluence user's password. Can also be specified by the 'CONFLUENCE_PASSWORD' environment variable.
        -v, --verbose                    Output more information
        -h, --help                       Display this screen

The script assumes that a page has already been created for the markdown to be uploaded to. I haven't looked into automating the initial creation of the page, but that would require some additional knowledge, like what the parent page should be, etc. I also acknowledge that this could be more tightly bundled into a standalone executable. [Pull requests](https://github.com/LanyonM/markdown-to-confluence-uploader/fork) are welcome!

# The Plumbing
There is quite a bit of arg parsing for the options discussed above, so I've cut to the interesting bits. On line 4 and 5, the script grabs the page that the markdown will be uploaded to. On line 14 and line 21 the conversion from markdown to [wiki format](https://confluence.atlassian.com/display/DOC/Confluence+Wiki+Markup) and then to [storage format](https://confluence.atlassian.com/display/DOC/Confluence+Storage+Format) is performed.

{% highlight ruby linenos %}
opts = options[:verbose] ? {} : {log: false}
cs = ConfluenceSoap.new("#{options[:server]}/rpc/soap-axis/confluenceservice-v2?wsdl", user, password, opts)

pages = cs.get_pages(options[:spaceName])
uploader_page = pages.detect { |page| page.id == options[:pageId] }

if uploader_page.nil?
  puts "exiting... could not find pageId: #{options[:pageId]}"
  exit
end

begin
  text = File.read(options[:markdownFile])
  @convertedText = "#{Kramdown::Document.new(text).to_confluence}"
rescue Exception => ex
  warn "There was an error running the converter: \n#{ex}"
end

@convertedText = "#{@convertedText}\n\n(rendered at #{Time.now.getutc} by md2confl)"

uploader_page.content = cs.convert_wiki_to_storage_format(@convertedText)
options = {minorEdit: true, versionComment: 'updated by md2confl'}
cs.update_page(uploader_page)
{% endhighlight %}

I had to contribute a couple changes to the [confluence-soap](https://github.com/intridea/confluence-soap) gem to make all this possible. It was my first time contributing to a Ruby project and I must say that I was impressed by the ease with which I was able to contribute.

