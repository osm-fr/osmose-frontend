%rss="http://"+website+"/byuser/"+username+".rss"
%rebase('layout.tpl', title=(_("Statistics for user %s") % ", ".join(users)), rss=rss)
<h1>{{_("User statistics for %s") % ", ".join(users)}}</h1>
<p>{{_("This page shows errors on elements that were last modified by '%s'. This doesn't means that this user is responsible for all these errors.") % "', '".join(users)}}</p>
<p><a href="{{rss}}">{{_("This list is also available via rss.")}}</a></p>
<p>
%if count < 500:
    {{_("Number of found errors: %d") % count}}
%else:
    {{_("Number of found errors: more than %d") % count}}
%end
 - 
<a href='../map/#username={{username}}'>{{_("Show errors on a map")}}</a>
</p>

%include("views/errors/list.tpl", errors=errors, gen="info", opt_date="-1", translate=translate)
