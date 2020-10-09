function checkwindow() {
	event.returnValue=false;
}

function get_connect_info() {
    var hostid = $.trim($('#hostid').text());
    var connect_info = 'hostid=' + hostid;
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
	
	// Terminal.applyAddon(attach);
	// Terminal.applyAddon(fit);
	// Terminal.applyAddon(fullscreen);
	// Terminal.applyAddon(search);
	// Terminal.applyAddon(terminado);
	// Terminal.applyAddon(webLinks);
	// Terminal.applyAddon(zmodem);

    //var term = new Terminal(
	term = new Terminal({
		  	rendererType: 'dom', // 渲染类型，canvas 与 dom, xterm v3 使用 canvas 会无法显示 _ ，故使用 dom，v4 版本就无此问题
      		scrollback: 12800, // 终端回滚量
            cols: cols,
            rows: rows,
            useStyle: true,
            cursorBlink: true,
			theme: {
				//background: '#008080',
				// background: '#272822',
				foreground: '#7e9192',
        		background: '#002833',
			},
        })
        protocol = (location.protocol === 'https:') ? 'wss://' : 'ws://';
        socketURL = protocol + location.hostname + ((location.port) ? (':' + location.port) : '') + '/ws/webssh/?' + connect_info + '&width=' + cols + '&height=' + rows;

	//var sock;
	sock = new WebSocket(socketURL);
	sock.binaryType = "arraybuffer";    // 必须设置，zmodem 才可以使用

	/*
    * status 为 0 时, 将用户输入的数据通过 websocket 传递给后台, data 为传递的数据, 忽略 cols 和 rows 参数
    * status 为 1 时, resize pty ssh 终端大小, cols 为每行显示的最大字数, rows 为每列显示的最大字数, 忽略 data 参数
    * status 为 2 时, 忽略数据，只是为了 zmodem 记录上传和下载记录
    */
    var message = {'status': 0, 'data': null, 'cols': null, 'rows': null};

	function uploadFile(zsession) {
        let uploadHtml = "<div>" +
            "<label class='upload-area' style='width:100%;text-align:center;' for='fupload'>" +
            "<input id='fupload' name='fupload' type='file' style='display:none;' multiple='true'>" +
            "<i class='fa fa-cloud-upload fa-3x'></i>" +
            "<br />" +
            "点击选择文件" +
            "</label>" +
            "<br />" +
            "<span style='margin-left:5px !important;' id='fileList'></span>" +
            "</div><div class='clearfix'></div>";

        let upload_dialog = bootbox.dialog({
            message: uploadHtml,
            title: "上传文件",
            buttons: {
				cancel: {
					label: '关闭',
					className: 'btn-default',
					callback: function (res) {
						try {
							// zsession 每 5s 发送一个 ZACK 包，5s 后会出现提示最后一个包是 ”ZACK“ 无法正常关闭
							// 这里直接设置 _last_header_name 为 ZRINIT，就可以强制关闭了
							zsession._last_header_name = "ZRINIT";
							zsession.close();
						} catch (e) {
							console.log(e);
						}
					}
				},
            },
			closeButton: false,
        });

        function hideModal() {
			upload_dialog.modal('hide');
		}

		let file_el = document.getElementById("fupload");

		return new Promise((res) => {
			file_el.onchange = function (e) {
				let files_obj = file_el.files;
				hideModal();
				let files = [];
				for (let i of files_obj) {
					if (i.size <= 2048 * 1024 * 1024) {
						files.push(i);
					} else {
						toastr.warning(`${i.name} 超过 2048 MB, 无法上传`);
						// console.log(i.name, i.size, '超过 2048 MB, 无法上传');
					}
				}
				if (files.length === 0) {
					try {
						// zsession 每 5s 发送一个 ZACK 包，5s 后会出现提示最后一个包是 ”ZACK“ 无法正常关闭
						// 这里直接设置 _last_header_name 为 ZRINIT，就可以强制关闭了
						zsession._last_header_name = "ZRINIT";
						zsession.close();
					} catch (e) {
						console.log(e);
					}
					return
				} else if (files.length >= 25) {
					toastr.warning("上传文件个数不能超过 25 个");
					try {
						// zsession 每 5s 发送一个 ZACK 包，5s 后会出现提示最后一个包是 ”ZACK“ 无法正常关闭
						// 这里直接设置 _last_header_name 为 ZRINIT，就可以强制关闭了
						zsession._last_header_name = "ZRINIT";
						zsession.close();
					} catch (e) {
						console.log(e);
					}
					return
				}
				// Zmodem.Browser.send_files(zsession, files, {
				Zmodem.Browser.send_block_files(zsession, files, {
						on_offer_response(obj, xfer) {
							if (xfer) {
								// term.write("\r\n");
							} else {
								term.write(obj.name + " was upload skipped\r\n");
							}
						},
						on_progress(obj, xfer) {
							updateProgress(xfer);
						},
						on_file_complete(obj) {
                            term.write("\r\n");
							sock.send(JSON.stringify({"status": 2, "data": obj.name + " was upload success\r\n"}));
						},
					}
				).then(zsession.close.bind(zsession), console.error.bind(console)
				).then(() => {
					res();
				});
			};
		});
    }

	function saveFile(xfer, buffer) {
		return Zmodem.Browser.save_to_disk(buffer, xfer.get_details().name);
	}

	function updateProgress(xfer) {
		let detail = xfer.get_details();
		let name = detail.name;
		let total = detail.size;
		let percent;
		if (total === 0) {
			percent = 100
		} else {
			percent = Math.round(xfer._file_offset / total * 100);
		}

		term.write("\r" + name + ": " + total + " " + xfer._file_offset + " " + percent + "%    ");
	}

	function downloadFile(zsession) {
		zsession.on("offer", function(xfer) {
			function on_form_submit() {
				if (xfer.get_details().size > 2048 * 1024 * 1024) {
					xfer.skip();
					toastr.warning(`${xfer.get_details().name} 超过 2048 MB, 无法下载`);
					return
				}
				let FILE_BUFFER = [];
				xfer.on("input", (payload) => {
					updateProgress(xfer);
					FILE_BUFFER.push( new Uint8Array(payload) );
				});

				xfer.accept().then(
					() => {
						saveFile(xfer, FILE_BUFFER);
						term.write("\r\n");
						sock.send(JSON.stringify({"status": 2, "data": xfer.get_details().name + " was download success\r\n"}));
					},
					console.error.bind(console)
				);
			}

			on_form_submit();

		});

		let promise = new Promise( (res) => {
			zsession.on("session_end", () => {
				res();
			});
		});

		zsession.start();
		return promise;
	}

	var zsentry = new Zmodem.Sentry( {
        to_terminal: function(octets) {},  //i.e. send to the terminal

        on_detect: function(detection) {
            let zsession = detection.confirm();
            let promise;
            if (zsession.type === "receive") {
                promise = downloadFile(zsession);
            } else {
                promise = uploadFile(zsession);
            }
            promise.catch( console.error.bind(console) ).then( () => {
                //
            });
        },

        on_retract: function() {},

        sender: function(octets) { sock.send(new Uint8Array(octets)) },
     });

    // 打开 websocket 连接, 打开 web 终端
    sock.addEventListener('open', function () {
        //$('#django-webssh-terminal').removeClass('hide');
		term.open(document.getElementById('terminal'));
		term.focus();
		term.resize(cols, rows);
		term.write('Connecting...\n\r');

		toastr.options.closeButton = false;
		toastr.options.showMethod = 'slideDown';
		toastr.options.hideMethod = 'fadeOut';
		toastr.options.closeMethod = 'fadeOut';
		toastr.options.timeOut = 5000;
		toastr.options.extendedTimeOut = 3000;
		// toastr.options.progressBar = true;
		toastr.options.positionClass = 'toast-bottom-center';
		toastr.info('行列值: ' + cols + ' x ' + rows);

		toastr.options.timeOut = 10000;
		toastr.options.extendedTimeOut = 3000;
		toastr.info('友情提醒: 如果窗口出现空白，可通过改变浏览器窗口大小修复');

		$("body").attr("onbeforeunload",'checkwindow()'); //增加刷新关闭提示属性
    });

    // 读取服务器端发送的数据并写入 web 终端
    sock.addEventListener('message', function (recv) {
    	if (typeof(recv.data) === 'string') {
			var data = JSON.parse(recv.data);
			var message = data.message;
			var status = data.status;
			if (status === 0) {
				term.write(message);
				//console.log(message);
			} else if (status === 1 || status === 2) {
				//window.location.reload() 端口连接后刷新页面
				//term.clear()
				term.write(message);
				$("body").removeAttr("onbeforeunload"); //删除刷新关闭提示属性
				$(".session-close").attr("hidden", true);
				$("#up").attr("hidden", true);
				$("#down").attr("hidden", true);
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
			} else if (status === 3) {		// 锁定会话
				toastr.options.closeButton = true;
				toastr.options.showMethod = 'slideDown';
				toastr.options.hideMethod = 'fadeOut';
				toastr.options.closeMethod = 'fadeOut';
				toastr.options.timeOut = 0;
				toastr.options.extendedTimeOut = 3000;
				toastr.options.progressBar = true;
				toastr.options.positionClass = 'toast-top-right';
				toastr.warning(message);
				$(".session-close").attr("hidden", true);
				$("#up").attr("hidden", true);
				$("#down").attr("hidden", true);
			} else if (status === 6) {		// 解锁会话
				toastr.options.closeButton = true;
				toastr.options.showMethod = 'slideDown';
				toastr.options.hideMethod = 'fadeOut';
				toastr.options.closeMethod = 'fadeOut';
				toastr.options.timeOut = 0;
				toastr.options.extendedTimeOut = 3000;
				toastr.options.progressBar = true;
				toastr.options.positionClass = 'toast-top-right';
				toastr.success(message);
				$(".session-close").attr("hidden", false);
				$("#up").attr("hidden", false);
				$("#down").attr("hidden", false);
			}
		} else {
			zsentry.consume(recv.data);
		}
    });

    // 向服务器端发送数据
    term.on('data', function (data) {
        sock.send(JSON.stringify({"status": 0, "data": data}));
    });

    var timer = 0;
    // 监听浏览器窗口, 根据浏览器窗口大小修改终端大小，延迟改变
    $(window).resize(function () {
    	clearTimeout(timer);
		timer = setTimeout(function() {
			let cols_rows = get_term_size();
			sock.send(JSON.stringify({"status": 1, "data": null, "cols": cols_rows.cols, "rows": cols_rows.rows}));
			term.resize(cols_rows.cols, cols_rows.rows)
			toastr.options.closeButton = false;
			toastr.options.showMethod = 'slideDown';
			toastr.options.hideMethod = 'fadeOut';
			toastr.options.closeMethod = 'fadeOut';
			toastr.options.timeOut = 3000;
			toastr.options.extendedTimeOut = 3000;
			// toastr.options.progressBar = true;
			toastr.options.positionClass = 'toast-bottom-center';
			toastr.info('行列值: ' + cols_rows.cols + ' x ' + cols_rows.rows);
		}, 130)
    })
}
