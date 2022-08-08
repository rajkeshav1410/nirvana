var related_song = {},
    upnext_song = {},
    now_playing = '';

var insertHtml = function(selector, html) {
    var targetElem = document.querySelector(selector);
    targetElem.innerHTML = html;
};

var insertProperty = function(string, propName, propValue) {
    var propToReplace = "{{" + propName + "}}";
    string = string
        .replace(new RegExp(propToReplace, "g"), propValue);
    return string;
};

var onclickEvent = function(selector, callback) {
    $(selector).on('click', callback);
}

var hide = function(selector) {
    $(selector).addClass('d-none');
}

var show = function(selector) {
    $(selector).removeClass('d-none');
}

var post = async function(url, data) {
    var response = await fetch(url, {
        method: 'POST',
        body: JSON.stringify(data),
        headers: {
            'Content-Type': 'application/json'
        }
    });
    response = await response.text();
    return response;
};

var showLoading = function(selector, color, size) {
    var html = `<div class='d-flex justify-content-center mt-5 center'>
    <div class='spinner-border' role='status'
    style='color:${color};width:${size}em;height:${size}em;'>
    <span class='sr-only'></span >
    </div></div>`;
    insertHtml(selector, html);
};

var loadHomePage = function() {
    show('.navbar');
    showLoading('#main-content', 'var(--primary-accent)', 3.5);
    post('/popularity?n=50', {})
        .then(res => JSON.parse(res))
        .then(res => {
            html = `<h1 class="d-flex mx-auto justify-content-center">Top 50 songs</h1>` + createSearchTable(res);
            insertHtml('#main-content', html);
        });
};

createSearchTable = function(res) {
    let html = `<div class="d-flex mx-auto justify-content-center" id="search-table"><table class="table table-hover table-dark mt-2">
                <tbody>`;
    for (i = 0; i < Object.keys(res).length; i++) {
        html += `<tr onclick="search_table_song(this)">
                    <td>${(i + 1) + '. ' + res[i]}</td>
                </tr>`;
    }
    html += `</tbody></table></div>`;
    return html;
}

createSongList = function(res, id) {
    let html = `<div class="list-group list-group-flush" id="${id}">`;
    for (i = 0; i < Object.keys(res).length; i++) {
        data = res[i].split(' - ');
        html += `<a class="list-group-item list-group-item-action" aria-current="true" alt="${res[i]}">
                    <div class="d-flex w-100 justify-content-between">
                        <h5 class="mb-1">${data[0]}</h5>
                        <small>5:30</small>
                    </div>
                    <p class="mb-1 next-song-artist">${data[1]}</p>
                </a>`;
    }
    return html + `</div>`;
};

var load_related_tab = function(song_name) {
    showLoading('#related-tab', 'var(--primary-accent)', 3.5);
    post('/related_song', {
            song_name: song_name
        })
        .then(res => JSON.parse(res))
        .then(res => {
            console.log(res);
            related_song = res;
            let song_list = createSongList(res, 'related-list');
            insertHtml('#related-tab', song_list);
            elem = $('#related-list a');
            for (i = 0; i < elem.length; i++) {
                elem[i].addEventListener('click', function() {
                    load_song_page($(this).attr('alt'));
                });
            }
        });
};

var load_next_song_tab = function(song_name) {
    showLoading('#upnext-tab', 'var(--primary-accent)', 3.5);
    post('/next_song', {
            song_name: song_name
        })
        .then(res => JSON.parse(res))
        .then(res => {
            upnext_song = res;
            let song_list = createSongList(res, 'upnext-list');
            insertHtml('#upnext-tab', song_list);
            elem = $('#upnext-list a');
            now_playing = elem[0];
            $(now_playing).toggleClass('active');
            for (i = 0; i < elem.length; i++) {
                elem[i].addEventListener('click', function() {
                    load_related_tab($(this).attr('alt'));
                    $(this).toggleClass('active');
                    $(now_playing).toggleClass('active');
                    now_playing = this;
                });
            }
        });
};

var load_song_page = function(song_name) {
    console.log(song_name);
    showLoading('#main-content', 'var(--primary-accent)', 3.5);
    $ajaxUtils.sendGetRequest(
        '/song_page',
        function(htmlData) {
            insertHtml('#main-content', htmlData);
            load_next_song_tab(song_name);
            load_related_tab(song_name);
        },
        false
    );
};

var search_table_song = function(elem) {
    load_song_page(elem.getElementsByTagName('td')[0].innerHTML.slice(3));
};

var search_song = function() {
    let song_name = document.getElementById('searchbar').value
    song_name = song_name.toLowerCase();
    showLoading('#main-content', 'var(--primary-accent)', 3.5);
    post('/search', {
            song_name: song_name
        })
        .then(res => JSON.parse(res))
        .then(res => {
            console.log(res);
            insertHtml('#main-content', createSearchTable(res));
        });
};

var loadSearchBox = function() {

};

onclickEvent('#search-button', loadSearchBox);

$(function() {
    loadHomePage();
});

gapi.load("client", loadClient);

function loadClient() {
    gapi.client.setApiKey("AIzaSyD_pABPB4xoVTZFG15ZIFIS-CtI8s5SLJg");
    return gapi.client.load("https://www.googleapis.com/discovery/v1/apis/youtube/v3/rest")
        .then(function() { console.log("GAPI client loaded for API"); },
            function(err) { console.error("Error loading GAPI client for API", err); });
}