from devops.celery import app
from webssh.models import TerminalLog


@app.task(ignore_result=True)
def celery_save_res_asciinema(res_file, res_asciinema, enter=True):
    if enter:
        with open(res_file, 'a+') as f:
            for line in res_asciinema:
                f.write('{}\n'.format(line))
    else:
        with open(res_file, 'a+') as f:
            for line in res_asciinema:
                f.write('{}'.format(line))


@app.task(ignore_result=True)
def celery_save_terminal_log(user, hostname, ip, protocol, port, username, cmd, detail, address, useragent, start_time):
    event = TerminalLog()
    event.user = user
    event.hostname = hostname
    event.ip = ip
    event.protocol = protocol
    event.port = port
    event.username = username
    event.cmd = cmd
    event.detail = detail
    event.address = address
    event.useragent = useragent
    event.start_time = start_time
    event.save()

