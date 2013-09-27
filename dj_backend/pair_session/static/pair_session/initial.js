$(function() {

  var lang_mode = {};
  var indentUnit = 4;
  switch(g_language) {
    case "javascript":
      lang_mode = {name: "javascript", json: true};
      indentUnit = 2;
      break;
    case "python":
      lang_mode = {name: "python"};
      indentUnit = 4;
      break;
    case "ruby":
      lang_mode = {name: "ruby"};
      indentUnit = 4;
      break;
  }

  var editor_default = {
    lineNumbers: true,
    mode: lang_mode,
    indentUnit: indentUnit,
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
        "<img src=\"{{ avatar_url }}\" width='28' height='28'>"+
        "<span class=\"color color-1\"></span>{{ username }}"+
        "<button class=\"btn-delete\"><i class=\"icon-remove\"></i></button>"+
        "</li>";
  var template_chat_list = "<li>"+
                "<img src=\"{{ avatar_url }}\" width='28' height='28'><span class=\"user\">{{ username }}</span>"+
                "<div>{{ message }}</div>"+
                "</li>";
  var template_result_list = "<li>"+
                "<pre>"+
                "  {{ result }}"+
                "<pre>"+
                "</li>";
  function log(msg) {
    console.log(msg);
  }

  var code_dirty = false;
  var remote_update = false;

  editor.on('change', function(cm, eventObj){
    if(conn === null) {
      return;
    }
    if(remote_update) {
      remote_update = false;
    }else{
      code_dirty = true;
    }
    
  });

  function code_updater() {
    if(code_dirty) {
      send_obj.type = 'code_update';
      send_obj.data = editor.getValue();
      send_obj.session = g_session_name;
      code_dirty = false;
      conn.send(JSON.stringify(send_obj));
    }
    setTimeout(code_updater, 500);
  }

  setTimeout(code_updater, 500);

  function connect() {
    disconnect();

    var transports = ["websocket", "xhr-streaming", "iframe-eventsource", "iframe-htmlfile", "xhr-polling", "iframe-xhr-polling", "jsonp-polling"];

    conn = new SockJS('http://'+window.location.hostname+':8888/chat', transports);

    log('Connecting...');

    conn.onopen = function() {
      log('Connected.');
      send_obj.type = 'session_join';
      send_obj.data = g_session_name;
      conn.send(JSON.stringify(send_obj));
      update_ui();
    };

    conn.onmessage = function(e) {
      recv_obj = JSON.parse(e.data);
      log('Received: ' + recv_obj);
      switch(recv_obj.type){
        case "code_update":
          remote_update = true;
          current_position = window.code_editor.getCursor();
          window.code_editor.setValue(recv_obj.data);
          window.code_editor.setCursor(current_position);
          break;
        case "session_list_update":
          users = JSON.parse(recv_obj.data);
          var user_list_html = '';
          users.map(function(user){
            user.static_root = g_static_root;
            if(user.avatar_url){
              user.avatar_url = user.avatar_url.split('?')[0];
            }
            user_list_html += Mustache.render(template_user_list, user);
          });
          $('ul.chat-list').html(user_list_html);
          break;
        case "chat_message_receive":
          chat_message = JSON.parse(recv_obj.data);
          if(chat_message.avatar_url){
            chat_message.avatar_url = chat_message.avatar_url.split('?')[0];
          }
          chat_message_html = Mustache.render(template_chat_list, chat_message);
          var $chatbox = $('ul.chat-wrapper');
          $chatbox.append(chat_message_html);
          $chatbox.scrollTop($chatbox[0].scrollHeight);
          break;
        case "run_code_result":
          result = JSON.parse(recv_obj.data);
          code_result_html = Mustache.render(template_result_list, result);
          var $result_list = $('ul.refs');
          $result_list.prepend(code_result_html);
          $result_list.scrollTop($result_list[0].scrollHeight);
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

  $('div.search-wrapper input.chat-message').keypress(function(event){
    if(event.keyCode != 13) {
      return;
    }
    $this = $(this);
    var message = $this.val();
    if(message === '')
      return;
    $this.val('');
    send_obj.type = 'chat_message_send';
    send_obj.data = message;
    send_obj.session = g_session_name;
    conn.send(JSON.stringify(send_obj));
  });

  $('button.run-button').click(function(){
    var code = editor.getValue();
    if(code === '')
      return;
    send_obj.type = 'run_code';
    send_obj.data = code;
    send_obj.language = g_language;
    send_obj.session = g_session_name;
    console.log(send_obj);
    conn.send(JSON.stringify(send_obj));
  });

  $(document).ready(function(){
    connect();
  });

});