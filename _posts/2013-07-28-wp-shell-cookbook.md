---
layout: post
title: "WP-Shell Chef Cookbook"
description: "A Chef application-style cookbook that installs a shell for WordPress"
category: articles
tags: [apache, chef, mysql, operations, ruby, software, vagrant, wordpress]
comments: true
---

<div class="center">
  <figure>
    <a href="/images/wp-shell-meme.jpg"><img src="/images/wp-shell-meme.jpg"></a>
    <figcaption>I don't usually use WordPress, but when I do, I configure it with Chef.</figcaption>
  </figure>
</div>

In fact, I've never done actual work in WordPress.  Unfortunately, a WP-based project at work isn't going so well, and we need to have team members ramp up super quick to be able to contribute.  WordPress needs Apache, MySQL and PHP to run, but there's no guarantee that a.) team members have those installed or b.) they won't have configuration conflicts.

# The Cookbook
Instead of telling everyone to install MAMP, I whipped up a Chef recipe and Vagrantfile that'll get an environment running quickly.  The [WP-Shell Cookbook](https://github.com/LanyonM/wp-shell) will install the necessary packages, create a virtualhost and import a database dump.  The cookbook assumes that the PHP code will reside on the host machine and that the database dump will be available during the first converge.

You can click through the link above to check out the code, but the one thing I wanted to highlight was the DB create.  I'm sure there's a better way to bootstrap the DB (and repopulate it if the data changes).  If you know of a way, please let me know.

{% highlight ruby linenos %}
# import the mysql data
execute "create-database" do
  command "mysql -u #{node['wp-shell']['db_user']} -p#{node['wp-shell']['db_password']} -e 'CREATE DATABASE IF NOT EXISTS #{node['wp-shell']['db_name']}' && mysql -u #{node['wp-shell']['db_user']} -p#{node['wp-shell']['db_password']} #{node['wp-shell']['db_name']} < #{node['wp-shell']['host-folder']}/#{node['wp-shell']['db-dump-name']}"
  not_if ("mysqlshow -u #{node['wp-shell']['db_user']} -p#{node['wp-shell']['db_password']} #{node['wp-shell']['db_name']} | grep wp_users")
end
{% endhighlight %}

You'll also notice that there's a reference to `'host-folder'`, which creates a syntactical tight coupling to the use of Vagrant.  I should probably put correcting that on the to-do list.

# The Vagrantfile
The Vagrantfile does more than it needs to, but a `vagrant up` takes roughly 12 minutes - about the amount of time it would take to grab a coffee.  Here are some of the key components in the Vagrantfile:

{% highlight ruby linenos %}
config.vm.synced_folder "<path_on_host_machine_to_database_dump>", "/home/vagrant/host"
config.vm.synced_folder "<path_on_host_machine_to_wp_src>", "/opt/wordpress"

config.vm.provision :chef_solo do |chef|
  chef.cookbooks_path = "cookbooks"
  chef.add_recipe 'wp-shell::default'

  chef.json = {
    'mysql' => {
      'server_root_password' => 'rootpass'
    },
    'wp-shell' => {
      'server_name' => 'wordpress.dev',
      'docroot' => '/opt/wordpress',
      'db_name' => 'wp_db_name'
    }
  }
end
{% endhighlight %}

It's really quite straightforward.  The two mounted paths are for the database dump and the WordPress code.  On line 12 in the `chef.json` I show how to set some of the cookbook attributes.  I had initially tried to do most of the work from within the Vagrantfile, but it fell apart when I wanted to create and enable the WP-specific virtualhost.

# In Conclusion
Hopefully this doesn't re-invent an existing solution - aside those like MAMP, LAMP or WAMP.  Help make it better: [fork it](https://github.com/LanyonM/wp-shell/fork) on GitHub.
