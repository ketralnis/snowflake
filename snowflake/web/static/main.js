$(function() {
    var cookie = Cookies.get('user_name');
    if(cookie) {
        // if they've used a name in the past, try to reuse it
        $('input[name=user_name]').val(cookie);
    }

    $.popup = null;

    get_next();

    $('.labels').click(function(evt) {
        var target = $(evt.target);

        var user_name = $('input[name=user_name]').val();
        var label = target.data('label');
        console.log(target);
        console.log(label);
        var url = $('input[name=url]').val();

        if(user_name.length <= 0) {
            alert("need a user name")
            return false;
        }

        // save this username
        Cookies.set("user_name", user_name);

        $.ajax({
            'url': '/rate',
            'method': 'POST',
            'data': {
                'who': user_name,
                'label': label,
                'url': url
            },
            'error': function(xhr, textStatus, errorThrown) {
                console.log("Err", xhr, textStatus, errorThrown);
                alert("Error!")
            },
            'success': get_next
        })
    })
})

function open_popup(href) {
    if($.popup) {
        $.popup.location = href;
    } else {
        $.popup = window.open(href, 'popup');
    }
}

function get_next() {
    $.ajax({
        url: "/next",
        dataType: 'json',
        method: 'GET',
        error: function(xhr, textStatus, errorThrown) {
            console.log("Err", xhr, textStatus, errorThrown);
            alert("Error!")
        },
        success: function(data, textStatus, xhr) {
            // clear out the labels so we can add the ones that came in
            $('.labels').empty();

            for(var i=0; i<data.labels.length; i++) {
                var label = data.labels[i];
                var span = document.createElement('span');
                span.setAttribute('class', 'btn');
                span.setAttribute('data-label', label);
                colorize(span, label);
                span.appendChild(document.createTextNode(label));
                $('.labels').append(span);
            }

            if(data.url) {
                $('input[name=url]').val(data.url)
                open_popup(data.url);
            } else {
                $('.url-container').hide()
                open_popup("about:blank");
            }
        }
    })
}


// I picked some colours that I can mostly differentiate
var david_colors = ["#FFE4C4", "#5F9EA0", "#90EE90", "#40E0D0", "#FA8072"];
var color_map = {'n': -1};

var color_mapped = function(name) {
    // allocate and memoise a color to be reused. this probably won't
    // be the same between requests but at least it will be the same on
    // the same refresh

    if(color_map[name]) {
        return color_map[name];
    } else if(color_map.n > david_colors+1) {
        return null;
    }
    color_map.n += 1;
    color_map[name] = david_colors[color_map.n++];
    return color_map[name];
}

var colorize = function(span, mapping_name) {
    var color = color_mapped(mapping_name);
    if(color) {
        span.setAttribute("style",
                          "background-color: "+color);
    }
}
