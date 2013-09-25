$(function() {

  var editor_default = {
    lineNumbers: true,
    mode: {name: "javascript", json: true},
    indentUnit: 2,
    indentWithTabs: false,
    enterMode: "keep",
    tabMode: "shift",
    theme: 'solarized dark'
  };
  var editor = CodeMirror.fromTextArea(document.getElementById("coding_area"),
    editor_default);

  window.code_editor = editor;

  var conn = null;
  var send_obj = {'type': undefined,
                   'data': null};

  var last_update_time = new Date();

  var template_user_list = "<li>"+
        "<img src=\"{{ user.avatar_url }}\" width='28' height='28'>"+
        "<span class=\"color color-1\"></span>{{ user.username }}"+
        "<button class=\"btn-delete\"><i class=\"icon-remove\"></i></button>"+
        "</li>";

  function log(msg) {
    console.log(msg);
  }

  editor.on('change', function(cm, eventObj){
    if(conn === null) {
      return;
    }
    var current_time = new Date();
    if(current_time - last_update_time < 500)
      return;
    else
      last_update_time = current_time;
    send_obj.type = 'code_update';
    send_obj.data = cm.getValue();
    send_obj.session = 'temp_session';
    conn.send(JSON.stringify(send_obj));
  });

  function connect() {
    disconnect();

    var transports = ["websocket", "xhr-streaming", "iframe-eventsource", "iframe-htmlfile", "xhr-polling", "iframe-xhr-polling", "jsonp-polling"];

    conn = new SockJS('http://'+window.location.hostname+':8888/chat', transports);

    log('Connecting...');

    conn.onopen = function() {
      log('Connected.');
      send_obj.type = 'session_join';
      send_obj.data = 'temp_session';
      conn.send(JSON.stringify(send_obj));
      update_ui();
    };

    conn.onmessage = function(e) {
      recv_obj = JSON.parse(e.data);
      log('Received: ' + recv_obj);
      switch(recv_obj.type){
        case "code_update":
          current_position = window.code_editor.getCursor();
          window.code_editor.setValue(recv_obj.data);
          window.code_editor.setCursor(current_position);
          break;
        case "session_list_update":
          users = JSON.parse(recv_obj.data);
          var user_list_html = '';
          users.map(function(user){
            user.static_root = g_static_root;
            user_list_html += Mustache.render(template_user_list, user);
          });
          $('ul.chat-list').html(user_list_html);
          break;
        default:
          break;
      }
    };

    conn.onclose = function() {
      log('Disconnected.');
      conn = null;
      update_ui();
    };
  }

  function disconnect() {
    if (conn !== null) {
      log('Disconnecting...');

      conn.close();
      conn = null;

      $('ul.chat-list').html('');

      update_ui();
    }
  }

  function update_ui() {
    var msg = '';

    if (conn === null || conn.readyState != SockJS.OPEN) {
      $('#status').text('disconnected');
      $('#connect').text('Connect');
    } else {
      $('#status').text('connected (' + conn.protocol + ')');
      $('#connect').text('Disconnect');
    }
  }

  $('button.join-talk').click(function() {
    if (conn === null) {
      connect();
      $('button.join-talk span.join-button-text').text('Disconnect');
    } else {
      disconnect();
      $('button.join-talk span.join-button-text').text('JOIN TALK');
    }
    update_ui();
    return false;
  });
});