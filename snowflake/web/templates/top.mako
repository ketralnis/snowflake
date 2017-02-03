<%! import json %>
<!DOCTYPE html>
<html>
    <head>
        <link rel="stylesheet" href="${static('bootstrap-3.3.7-dist/css/bootstrap.min.css')}" />
        <link rel="stylesheet" type="text/css" href="${static('style.css')}" />

        <script type="text/javascript" src="${static('jquery-1.12.0.min.js')}"></script>
        <script type="text/javascript" src="${static('js.cookie.js')}"></script>
        <script type="text/javascript" src="${static('main.js')}"></script>

        <script type="text/javascript">//<![CDATA[

        // TODO this doesn't work, also mako default filters?
        $.config = ${json.dumps(config or {})|n}

        //]]></script>
    </head>
    <body>
        <span class="welcome-container">
            user name <input name="user_name" value="${default_name}" />
        </span>

        <span class="url-container">
            url: <input readonly="readonly" name="url" value="(loading...)"/>
        </span>

        <span class="labels-container">
            labels: <span class="labels">(loading...)</span>
        </span>

        <span class="go btn btn-info">
            get started
        </span>

        <span class="skip btn btn-info">
            skip
        </span>
    </body>
</html>
