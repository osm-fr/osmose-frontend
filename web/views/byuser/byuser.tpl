%rss="https://"+website+"/byuser/"+username+".rss"
%rebase('layout.tpl', title=(_("Statistics for user %s") % ", ".join(users)), rss=rss)
<h1>{{_("User statistics for %s") % ", ".join(users)}}</h1>
<p>{{_("This page shows issues on elements that were last modified by '%s'. This doesn't means that this user is responsible for all these issues.") % "', '".join(users)}}</p>
<p><a href="{{rss}}">{{_("This list is also available via rss.")}}</a></p>
<p>
%if count < 500:
    {{_("Number of found issues: %d") % count}}
%else:
    {{_("Number of found issues: more than %d") % count}}
%end
 - 
<a href='../map/#username={{username}}'>{{_("Show issues on a map")}}</a>
</p>

%include("web/views/errors/list.tpl", query="", errors=errors, gen="info", opt_date="-1", page_args="username=%s&" % html_escape(username))
