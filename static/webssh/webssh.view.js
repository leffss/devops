function checkwindow() {
	event.returnValue=false;
}

function get_connect_info() {
    var group = $.trim($('#group').text());
    var connect_info = 'group=' + group;
    return connect_info
}

function get_term_size() {
    var init_width = 9;
    var init_height = 17;

    var windows_width = $(window).width();
    var windows_height = $(window).height();
	var headers_height = $("#headers").height();

    return {
        cols: Math.floor(windows_width / init_width),
        rows: Math.floor((windows_height - headers_height) / init_height),
    }
}

function websocket() {
    var cols = get_term_size().cols;
    var rows = get_term_size().rows;
    var connect_info = get_connect_info();

    var term = new Terminal(
        {
            cols: cols,
            rows: rows,
            useStyle: true,
            cursorBlink: true,
			theme: {
				//background: '#008080',
				background: '#272822',
			},
        }
        ),
        protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://',
        socketURL = protocol + location.hostname + ((location.port) ? (':' + location.port) : '') + '/webssh/view/?' + connect_info;

    var sock;
    sock = new WebSocket(socketURL);

    // 打开 websocket 连接, 打开 web 终端
    sock.addEventListener('open', function () {
        //$('#django-webssh-terminal').removeClass('hide');
        term.open(document.getElementById('terminal'));
		//term.focus();
		//term.write('Connecting...\n\r');
		$("body").attr("onbeforeunload",'checkwindow()'); //增加刷新关闭提示属性
		
    });

    // 读取服务器端发送的数据并写入 web 终端
    sock.addEventListener('message', function (recv) {
        var data = JSON.parse(recv.data);
        var message = data.message;
        var status = data.status;
        if (status === 0) {
            term.write(message)
        } else if (status === 1 || status === 2 ) {
            //window.location.reload() 端口连接后刷新页面
			//term.clear()
			term.write(message)
			$("body").removeAttr("onbeforeunload"); //删除刷新关闭提示属性
			$("#session-close").attr("hidden", true);
			$("#session-unlock").attr("hidden", true);
			$("#session-lock").attr("hidden", true);
			toastr.options.closeButton = true;
			toastr.options.showMethod = 'slideDown';
			toastr.options.hideMethod = 'fadeOut';
			toastr.options.closeMethod = 'fadeOut';
			toastr.options.timeOut = 0;	
			toastr.options.extendedTimeOut = 3000;	
			toastr.options.progressBar = true;
			toastr.options.positionClass = 'toast-top-right';
			toastr.error(message);
			//$(document).keyup(function(event){	// 监听回车按键事件
			//	if(event.keyCode == 13){
					//window.location.reload();
			//	}
			//});
			//term.dispose()
			//$('#django-webssh-terminal').addClass('hide');
			//$('#form').removeClass('hide');
        } else if (status === 3 ) {
			toastr.options.closeButton = true;
			toastr.options.showMethod = 'slideDown';
			toastr.options.hideMethod = 'fadeOut';
			toastr.options.closeMethod = 'fadeOut';
			toastr.options.timeOut = 0;	
			toastr.options.extendedTimeOut = 0;	
			toastr.options.progressBar = true;
			toastr.options.positionClass = 'toast-top-right'; 
			toastr.warning(message);
		} else if (status === 5 ) {
			term.write(message)
		};
    });

    /*
    * status 为 0 时, 将用户输入的数据通过 websocket 传递给后台, data 为传递的数据, 忽略 cols 和 rows 参数
    * status 为 1 时, resize pty ssh 终端大小, cols 为每行显示的最大字数, rows 为每列显示的最大字数, 忽略 data 参数
    */
    var message = {'status': 0, 'data': null, 'cols': null, 'rows': null};
	
    // 向服务器端发送数据
    term.on('data', function (data) {
        //message['status'] = 0;
        //message['data'] = data;
        //var send_data = JSON.stringify(message);
        //sock.send(send_data);
    });

    // 监听浏览器窗口, 根据浏览器窗口大小修改终端大小
    $(window).resize(function () {
        var cols = get_term_size().cols;
        var rows = get_term_size().rows;
        //message['status'] = 1;
        //message['cols'] = cols;
        //message['rows'] = rows;
        //var send_data = JSON.stringify(message);
        //sock.send(send_data);
        term.resize(cols, rows)
    })
}
