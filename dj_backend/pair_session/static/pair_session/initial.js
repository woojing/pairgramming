;(function(){
  var editor = CodeMirror.fromTextArea(document.getElementById("coding_area"), {
    lineNumbers: true,
    mode: "javascript",
    indentUnit: 2,
    indentWithTabs: false,
    enterMode: "keep",
    tabMode: "shift",
    theme: 'solarized dark'
  });
})();

$(function() {
  var conn = null;

  function log(msg) {
    var control = $('#log');
    control.html(control.html() + msg + '<br/>');
    control.scrollTop(control.scrollTop() + 1000);
  }

  function connect() {
    disconnect();

    var transports = $('#protocols input:checked').map(function() {
      return $(this).attr('id');
    }).get();

    conn = new SockJS('http://' + window.location.host + '/chat', transports);

    log('Connecting...');

    conn.onopen = function() {
      log('Connected.');
      conn.send('room:' + jQuery('#roomnumber').val())
      update_ui();
    };

    conn.onmessage = function(e) {
      log('Received: ' + e.data);
    };

    conn.onclose = function() {
      log('Disconnected.');
      conn = null;
      update_ui();
    };
  }

  function disconnect() {
    if (conn != null) {
      log('Disconnecting...');

      conn.close();
      conn = null;

      update_ui();
    }
  }

  function update_ui() {
    var msg = '';

    if (conn == null || conn.readyState != SockJS.OPEN) {
      $('#status').text('disconnected');
      $('#connect').text('Connect');
    } else {
      $('#status').text('connected (' + conn.protocol + ')');
      $('#connect').text('Disconnect');
    }
  }

  $('#connect').click(function() {
    if (conn == null) {
      connect();
    } else {
      disconnect();
    }

    update_ui();
    return false;
  });

  $('form').submit(function() {
    var text = $('#text').val();
    log('Sending: ' + text);
    text = 'my_room:' + jQuery('#roomnumber').val() + ',' + text;
    conn.send(text);
    $('#text').val('').focus();
    return false;
  });
});