---
layout: page
title: ASK Module
permalink: /ask-module/
---

{% assign mod = site.data.ask.training-module %}

authors:

{% for author in mod.authors %}
* {{ author.name }}
{% endfor %}

release: {{ mod.release }}

tools:

{% for tool in mod.tools %}
* {{ tool.name }} (q: {{ tool.quantity }}) {% if tool.new-key %} - new-key is set and has value {{ tool.new-key }} {% endif %}
{% endfor %}

materials:

{% for material in mod.materials %}
* {{ material.name }} (q: {{ material.quantity }})
{% endfor %}
