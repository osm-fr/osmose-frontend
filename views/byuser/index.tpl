%rebase('layout.tpl', title=_("Statistics for user"))
<h1>{{_("User statistics")}}</h1>
{{_("Osmose allows you to control your own errors.")}}<br>
{{_("By entering your OSM username in the following form, you will be able to see errors that are attached to your username. Note that the algorithm that attaches errors to username is not perfect, as Osmose only checks the last contributor of the relevant erroneous elements.")}}
<br><br>
<form method='GET' action='#'>
<label for='username'>{{_("Username:")}}</label>
<input type='text' name='username' id='username'>
<input type='submit'>
</form>
