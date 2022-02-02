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
        # fileObj = tempfile.NamedTemporaryFile()
        # try:
        #     with open(filename, "w") as file:
        #         smb.smbClient.retrieveFile('\\\msfadmin',filename,fileObj, timeout=600)
        #         print(filename + " has been downloaded in current directory")

        # except Exception as e:
        #     print(e)
        # finally:
        #     fileObj.close() 
        # try:
        #     for share in smb.smbClient.listShares():
        #         print("[*] Share name:  %s " % share.name + '=> ' + share.comments)
        #         filelist = smb.smbClient.listPath(share.name,'/')
        #         for f in filelist:
        #             print("[*] Found : %s " % f.filename)
        #         print('')
        #         print('--------------------------------')
        #         print('')
        # except Exception:
        #     print("Failed to list this share")
        # finally:
        #     pathselect = typer.prompt("In which share do you want to download a file ? (just type name of file) ")
        #     filename = typer.prompt("Which file do you want to download ? (just type name of file) ")
        #     fileObj = tempfile.NamedTemporaryFile()
        #     try:
        #         with open(filename, "wb") as file:
        #             smb.smbClient.retrieveFile(pathselect,filename,fileObj)
        #         print(filename + " has been downloaded in current directory")
        #         fileObj.close()    
        #     except Exception:
        #         print('failed to download file')
        #         return False
        # return True
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
    typer.prompt("What do you want to do now ?")
    raise typer.Exit()

@app.command()
def ftp(
        host: Optional[str] = typer.Option(..., "-h", help="Ip or hostname of target."),
        username: Optional[str] = typer.Option(..., "-u"),
        password: Optional[str] = typer.Option(..., "-pwd"),
        port: Optional[int] = typer.Option(21, "-p")):
    try:
        ftp = FTP(host)
    except:
        print("Invalid host")
        exit()

    ftp.login(username, password)  # user anonymous, passwd anonymous@
    welcomeMessage = ftp.getwelcome()
    print(welcomeMessage)
    print('[+] 230 Login successful.')
    print('Root directory : ')
    ftp.cwd('./')
    ftp.retrlines('LIST')
    ftp.quit()

if __name__ == "__main__":
    app()