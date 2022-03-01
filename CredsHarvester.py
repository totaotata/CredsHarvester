import logging
import typer
from ftplib import FTP
from typing import Optional
import paramiko
from smb.SMBConnection import SMBConnection
from stat import S_ISDIR, S_ISREG
import tempfile
from io import StringIO
from pathlib import Path


app = typer.Typer()

@app.command()
def smb(IP: Optional[str] = typer.Option(..., "-h"),         username: Optional[str] = typer.Option(..., "-u"),
         password: Optional[str] = typer.Option(..., "-p"),
         port: Optional[str] = typer.Option(139, "-P"),
         ext_file: Optional[Path] = typer.Option(None, "-w")):

    conn = SMBConnection(username, password, "", "")

    def parse_file(share, filename, IP):
        if ext_file is None:
                typer.echo("No config file")
                raise typer.Abort()
        if ext_file.is_file():
            text = ext_file.read_text()
            file_ext = (filename.split('/')[-1]).split('.')[-1] or "empty"

            if file_ext.lower() in text:
                typer.secho("Found interesting file: " + filename, fg=typer.colors.GREEN)
                # print(ext_file.read_text())

        elif ext_file.is_dir():
            typer.echo("Config is a directory, will use all its config files")
        elif not ext_file.exists():
            typer.echo("The config doesn't exist")

            line_counter = 0 
            hits = 0 
            file_obj = tempfile.NamedTemporaryFile()
           
            #    self.db.insertFileFinding(filename, share, IP, retrieveTimes(share,filename))

    def explore_path(path,shared_folder,IP):
           #print (depth)
           try:
             for p in conn.listPath(shared_folder, path):
                 if p.filename!='.' and p.filename!='..':
                     parentPath = path
                     if not parentPath.endswith('/'):
                         parentPath += '/'
                     if p.isDirectory:   
                        # print(" Goto Directory => ", parentPath+p.filename)
                        explore_path(parentPath+p.filename,shared_folder,IP)        
                     else:
                        #  print( 'File found, go parsing : '+ parentPath+p.filename)
                         
                         parse_file(shared_folder, parentPath+p.filename, IP)
           except Exception as e: 
              print("Error while listing paths in shares: " + str(e))
        
    def connect(conn):
        try:
            conn.connect(IP, port)
            print("[+] SMB Connection Success on ", IP)
        except Exception as e:
             logging.warning("Detected error while connecting to " + str(IP) + " with message " + str(e))
        try:   
            shares = conn.listShares()
        except Exception as e:
            logging.warning("Detected error while listing shares on "  + str(IP) + " with message " + str(e))

        for share in shares:
            if not share.isSpecial and share.name not in ['NETLOGON', 'IPC$', "ADMIN$"]:
                print("[*] Share name:  %s " % share.name + '=> ' + share.comments)
                print('Listing file in share: ' + share.name)
                explore_path("/",share.name,IP)
    connect(conn)
   

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