import typer
from ftplib import FTP
from typing import Optional
import paramiko
from smb.SMBConnection import SMBConnection
from stat import S_ISDIR, S_ISREG
import tempfile
import traceback
import sys
from io import StringIO
app = typer.Typer()

@app.command()
def smb(host: Optional[str] = typer.Option(..., "-h"),
         username: Optional[str] = typer.Option(..., "-u"),
         password: Optional[str] = typer.Option(..., "-pwd"),
         port: Optional[str] = typer.Option(139, "-P")):

    smb.smbClient = SMBConnection(username, password, "", "")
    if smb.smbClient.connect(host, port):
        print("[+] SMB Connection Success ... ")
        print("[+] Listing the Shared resources")
        filelist = smb.smbClient.listPath('msfadmin','/')

        for share in smb.smbClient.listShares():
             print("[*] Share name:  %s " % share.name + '=> ' + share.comments)
        for f in filelist:
                print("[*] Found : %s " % f.filename)
        filename = typer.prompt("Which file do you want to download ? (just type name of file) ")
        print('Download = ' + '/' + filename)
        attr = smb.smbClient.getAttributes('msfadmin', '/'+filename)
        print('Size = %.1f kB' % (attr.file_size / 1024.0))
        print('start download')
        file_obj = tempfile.NamedTemporaryFile()
        file_attributes, filesize = smb.smbClient.retrieveFile('msfadmin', '/'+filename, file_obj)
        fw = open(filename, 'wb')
        file_obj.seek(0)
        for line in file_obj:
            fw.write(line)
            fw.close()
        print('download finished')
        smb.smbClient.close()
    else:
        print('Bad id/connection')
        return False

@app.command()
def ssh(host: Optional[str] = typer.Option(..., "-h"),
        username: Optional[str] = typer.Option(..., "-u"),
        password: Optional[str] = typer.Option(..., "-pwd"),
        port: Optional[int] = typer.Option(22, "-P")):
    command = "ls"
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, port, username, password, banner_timeout=5000)
    stdin, stdout, stderr = ssh.exec_command(command)
    lines = stdout.readlines()
    print(lines)

@app.command()
@app.command()
def sftp(host: Optional[str] = typer.Option(..., "-h"),
        username: Optional[str] = typer.Option(..., "-u"),
        password: Optional[str] = typer.Option(..., "-pwd"),
        port: Optional[int] = typer.Option(22, "-P")):
    command = "ls"
    transport = paramiko.Transport((host, port))
    transport.connect(None, username, password)
    sftp = paramiko.SFTPClient.from_transport(transport)
    print(sftp.listdir(path='.'))
    print('--------')
    for entry in sftp.listdir_attr(path='.'):
        mode = entry.st_mode
        if S_ISDIR(mode):
            print(entry.filename + "/")
        elif S_ISREG(mode):
            print(entry.filename + "")
    filename = typer.prompt("Which file do you want to download ?")
    try:
        sftp.get("./"+filename, ".\\"+filename)
    except:
        print("Error : download fail")
    raise typer.Exit()

@app.command()
def ftp(
        host: Optional[str] = typer.Option(..., "-h", help="Ip or hostname of target."),
        username: Optional[str] = typer.Option(..., "-u", help="Username"),
        password: Optional[str] = typer.Option(..., "-pwd", help="Password"),
        port: Optional[int] = typer.Option(21, "-p")):
    try:
        ftp = FTP(host) # connexion à l'hôte
    except:
        print("Invalid host")
        exit()

    try:
        ftp.login(username, password)  # user anonymous, passwd anonymous@
    except:
        print("Invalid username/password")
        exit()
    welcomeMessage = ftp.getwelcome()
    print(welcomeMessage)
    print('[+] 230 Login successful.')
    print('Root directory : ')
    try:
        ftp.cwd('./')
        ftp.retrlines('LIST')
        filename = typer.prompt("Which file do you want to download ?")
        with open(filename, "wb") as file:
            ftp.retrbinary("RETR " + filename, file.write)
    except:
        print('error')
    ftp.quit()

if __name__ == "__main__":
    app()