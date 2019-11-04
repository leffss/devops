import paramiko


def upload(now, total):
    print('\r总大：{0} 上传：{1}'.format(total, now), end='')
    if total <= now:
        print()


# 实例化一个transport对象
trans = paramiko.Transport(('192.168.223.111', 22))

# 建立连接
trans.connect(username='root', password='123456')

# 实例化一个 sftp对象,指定连接的通道
sftp = paramiko.SFTPClient.from_transport(trans)

# 发送文件
sftp.put(localpath='./devops.zip', remotepath='/root/devops.zip', callback=upload)

# 将sshclient的对象的transport指定为以上的trans
ssh = paramiko.SSHClient()
ssh._transport = trans
# 执行命令，和传统方法一样
stdin, stdout, stderr = ssh.exec_command('cd /root;unzip -oq devops.zip;cd devops;/bin/sh start_docker.sh')
print(stdout.read().decode())

# 关闭连接
trans.close()
