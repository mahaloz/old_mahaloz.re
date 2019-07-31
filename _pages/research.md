---
title: "Posts by Category"
layout: research
permalink: /research/
category: research
author_profile: true
---
{% for post in site.categories.research %}
 <li><span>{{ post.date | date_to_string }}</span> &nbsp; <a href="{{ post.url }}">{{ post.title }}</a></li>
{% endfor %}
