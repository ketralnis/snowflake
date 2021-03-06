$(function() {
    var cookie = Cookies.get('user_name');
    if(cookie) {
        // if they've used a name in the past, try to reuse it
        $('input[name=user_name]').val(cookie);
    }

    $('.labels-container,.url-container,.skip').hide()

    $.popup = null;

    $('.skip,.go').click(get_next);

    $('.labels').click(function(evt) {
        var target = $(evt.target);

        var user_name = $('input[name=user_name]').val();
        var label = target.data('label');
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

    $('.refresh').click(function() {
        var url = $('input[name=url]').val()
        open_popup(url);
        return false;
    })

    $('input[name=url]').focus(function() {
        $(this).select();
    })
})

function open_popup(href, mode) {
    mode = mode || 'popup';

    if(mode=='popup') {
        if($.popup && $.popup.closed) {
            $.popup = null;
        }

        if($.popup) {
            $.popup.location = href;
        } else {
            $.popup = window.open(href, '_blank', 'height=600,width=600');
            $.popup.location = href;
        }
    } else if(mode == 'frame') {
        // otherwise we're using the frame system
        window.frames.bottom.location = href;
    }
}

function get_next() {
    $('.welcome-container,.labels-container,.url-container,.skip').show()
    $('.go').hide();

    var user_name = $('input[name=user_name]').val();
    var url = '/next';

    if(!user_name || user_name.length==0) {
        // we're just requiring it now
        alert("need a user name");
        return false;
    }

    if(user_name && user_name.length>0) {
        // if we have a username, pass it along
        url = '/next?user_name='+escape(user_name);
    }

    $.ajax({
        'url': url,
        'dataType': 'json',
        'method': 'GET',
        'error': function(xhr, textStatus, errorThrown) {
            console.log("Err", xhr, textStatus, errorThrown);
            alert("Error!")
        },
        'success': function(data, textStatus, xhr) {
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
                $('.refresh').attr('href', data.url);
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
