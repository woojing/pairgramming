;(function(){
  
})();

$(function() {

  var editor = CodeMirror.fromTextArea(document.getElementById("coding_area"), {
    lineNumbers: true,
    mode: "javascript",
    indentUnit: 2,
    indentWithTabs: false,
    enterMode: "keep",
    tabMode: "shift",
    theme: 'solarized dark'
  });

  window.code_editor = editor;

  var conn = null;

  function log(msg) {
    console.log(msg);
  }

  function connect() {
    disconnect();

    var transports = ["websocket", "xhr-streaming", "iframe-eventsource", "iframe-htmlfile", "xhr-polling", "iframe-xhr-polling", "jsonp-polling"];

    conn = new SockJS('http://localhost:8888/chat', transports);

    log('Connecting...');

    conn.onopen = function() {
      log('Connected.');
      conn.send('session:temp_session');
      update_ui();
    };

    conn.onmessage = function(e) {
      recv_obj = JSON.parse(e.data);
      log('Received: ' + recv_obj);
      switch(recv_obj.type){
        case "code_update":
          window.code_editor.setValue(recv_obj.data);
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
    } else {
      disconnect();
    }
    update_ui();
    return false;
  });
});