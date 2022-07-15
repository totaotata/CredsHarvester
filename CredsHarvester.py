import logging
from termios import VDISCARD
from numpy import vectorize
import typer
from ftplib import FTP
from typing import Optional
import paramiko
from smb.SMBConnection import SMBConnection
from stat import S_ISDIR, S_ISREG
import tempfile
from io import StringIO
from pathlib import Path
import textract
import re
import os
import csv

app = typer.Typer()

# init csv
header = ['ShareName', 'Type', 'Path', 'Item found']
with open('export.csv', 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    # write the header
    writer.writerow(header)

# common function
def exportCSV(share, type, path, item):
    try:
        data = [share, type, path, item]
        with open('export.csv', 'a', encoding='UTF8') as f:
            writer = csv.writer(f)
            writer.writerow(data)
    except Exception as e:
        typer.echo("Detected error while write in CSV with message " + str(e))

def searchRegex(content, share, filename, regex_file):
    type = "REGEX"
    with open(regex_file) as f:
        # Here f is the file-like object
        read_data = f.read().split('\n')
    if regex_file.is_file():
        for item in read_data:
            x = re.findall(item, content)
            if x:
                typer.secho("[REGEX] Found '" + str(x) + "'  in : " +
                            filename, fg=typer.colors.BRIGHT_YELLOW)
                exportCSV(share, type, filename, x)


def searchKeywords(content, share, filename, keywords_file):
    type = "KEYWORD"
    with open(keywords_file) as f:
        # Here f is the file-like object
        read_data = f.read().split('\n')
    if keywords_file.is_file():
        for item in read_data:
            match = False
            if item in content:
                match = True
            if match:
                typer.secho("[KEYWORD] Found '" + item + "' keywords in : " +
                            filename, fg=typer.colors.GREEN)
                exportCSV(share, type, filename, item)


def filter_by_ext(share, filename, IP, ext_file, keywords_file, conn, regex_file):
    file_obj = tempfile.NamedTemporaryFile()
    file_ext = (filename.split('/')[-1]).split('.')[-1] or "empty"

    if ext_file.is_file():
        text = ext_file.read_text()
        if file_ext.lower() in text:
            # display all files with extension with -v arguments
            # typer.secho("Found interesting extension: " +
            #             filename, fg=typer.colors.WHITE)
            if keywords_file:
                if file_ext.lower() in ['docx', 'doc', 'zip', 'eml', 'epub', 'gif', 'jpg', 'mp3', 'msg', 'odt', 'ogg', 'pdf', 'png', 'pptx', 'ps', 'rtf', 'tiff', 'tif', 'wav', 'xlsx', 'xls']:
                    file = filename.split('/')[-1]
                    try:
                        with open(file, 'wb') as f:
                            conn.retrieveFile(share, filename, f)
                            content = textract.process(f.name)
                            content = content.decode(
                                "utf-8").replace("\n", " ").lower()
                            # typer.echo(content)
                            if len(content) > 0:
                                searchKeywords(
                                    content, share, filename, keywords_file)
                                searchRegex(content, share,
                                            filename, regex_file)
                            os.remove(f.name)
                    except Exception as e:
                        typer.echo("Detected error while read file " +
                                   f.name + " with message " + str(e))
                        os.remove(f.name)

                # if other file type
                else:
                    try:
                        with tempfile.NamedTemporaryFile() as file_obj:
                            conn.retrieveFile(share, filename, file_obj)
                            file_obj.seek(0)
                            content = file_obj.read()
                            content = content.decode(
                                'utf-8', 'ignore').translate({ord('\u0000'): None})
                            if len(content) > 0:
                                searchKeywords(
                                    content, share, filename, keywords_file)
                                searchRegex(content, share,
                                            filename, regex_file)
                            file_obj.close()
                    except Exception as e:
                        typer.echo("Detected error while read file " +
                                   filename + " with message " + str(e))
                        file_obj.close()

            file_obj.close()
        elif ext_file.is_dir():
            typer.echo(
                "Config is a directory, will use all its config files")
        #    Add to BDD


@app.command()
def smb(IP: Optional[str] = typer.Option(..., "-h"),
        username: Optional[str] = typer.Option(..., "-u"),
        password: Optional[str] = typer.Option(..., "-p"),
        domainName: Optional[str] = typer.Option(None, "-d"),
        port: Optional[str] = typer.Option(445, "-P"),
        ext_file: Optional[Path] = typer.Option(None, "-w", ),
        regex_file: Optional[Path] = typer.Option(None, "-r", ),
        entrypoint: Optional[str] = typer.Option('/', "--path"),
        keywords_file: Optional[Path] = typer.Option(None, "-k")):

    if not domainName:
        conn = SMBConnection(username, password, 'user', 'user', is_direct_tcp=True)
    else:
        conn = SMBConnection(username, password, 'user', 'user', domain=domainName, use_ntlm_v2=True,
                             sign_options=SMBConnection.SIGN_WHEN_SUPPORTED, is_direct_tcp=True)

    def explore_path(path, shared_folder, IP):
        try:
            for p in conn.listPath(shared_folder, path):
                if p.filename != '.' and p.filename != '..':
                    parentPath = path
                    if not parentPath.endswith('/'):
                        parentPath += '/'
                    if p.isDirectory:
                        # print(" Goto Directory => ", parentPath+p.filename)
                        explore_path(parentPath+p.filename, shared_folder, IP)
                    else:
                        #  print( 'File found, go parsing : '+ parentPath+p.filename)
                        filter_by_ext(shared_folder, parentPath +
                                      p.filename, IP, ext_file, keywords_file, conn, regex_file)
        except Exception as e:
            print("Error while listing paths in shares: " + path)

    def connect(conn):
        try:
            conn.connect(IP, port)
            typer.secho("[+] SMB Connection Success on " +
                        IP, fg=typer.colors.GREEN)

        except Exception as e:
            logging.warning("[-] Detected error while connecting to " +
                            str(IP) + " with message " + str(e) + "try again")
            exit()
        try:
            # path = conn.listPath()
            # print(path)
            shares = conn.listShares(timeout=30)
            if shares:
                for share in shares:
                    if not share.isSpecial and share.name not in ['NETLOGON', 'IPC$', "ADMIN$"]:
                        print("[*] Share name:  %s " %
                              share.name + '=> ' + share.comments)
                        print('Listing file in share: ' + share.name)
                        explore_path(entrypoint, share.name, IP)
        except Exception as e:
            logging.warning("Detected error while listing shares on " +
                            str(IP) + " with message " + str(e))

    connect(conn)


@app.command()
def sftp(host: Optional[str] = typer.Option(..., "-h"),
         username: Optional[str] = typer.Option(..., "-u"),
         password: Optional[str] = typer.Option(..., "-p"),
         port: Optional[int] = typer.Option(22, "-P"),
         ext_file: Optional[Path] = typer.Option(None, "-w"),
         keywords_file: Optional[Path] = typer.Option(None, "-k")):

    interesting_file = []

    try:
        transport = paramiko.Transport((host, port))
    except Exception as e:
        print("Erreur lors de la connection : " + e)
        exit()

    def filename_contains(filename, liste):
        liste = liste.split('\n')
        for text in liste:
            if text != "" and text in filename.lower():
                print("text : " + text + " , filename : " + filename.lower())
                return True
        return False

    def parse_file(path, filename):
        if ext_file is None:
            typer.echo("No config file")
            raise typer.Abort()
        if ext_file.is_file():
            text = ext_file.read_text()
            file_ext = (filename.split('/')[-1]).split('.')[-1] or "empty"
            file_name = (filename.split('/')[-1]) or "empty"

        if (file_ext.lower() in text) or (filename_contains(file_name, text)):
            interesting_file.append(filename)
            typer.secho("Found interesting file: " +
                        filename, fg=typer.colors.GREEN)
            # print(ext_file.read_text())

        elif ext_file.is_dir():
            typer.echo("Config is a directory, will use all its config files")
        elif not ext_file.exists():
            typer.echo("The config doesn't exist")

            line_counter = 0
            hits = 0
            file_obj = tempfile.NamedTemporaryFile()

            #    self.db.insertFileFinding(filename, share, IP, retrieveTimes(share,filename))

    def explore_path(sftp, path):
        # print(sftp.listdir(path='.'))
        # print('--------')
        for entry in sftp.listdir_attr(path):
            mode = entry.st_mode
            if S_ISDIR(mode):
                # print(entry.filename + "/")
                print("Goto Directory => " + entry.filename + "/")
                explore_path(sftp, path + entry.filename + "/")
            elif S_ISREG(mode):
                print(' File found, go parsing : ' + entry.filename)
                parse_file(path, entry.filename)
                return 1

    def connect(transport, username, password):
        try:
            transport.connect(None, username, password)
        except Exception as e:
            print("Invalid username/password (" + e + ")")
            exit()
        try:
            sftp = paramiko.SFTPClient.from_transport(transport)
        except Exception as e:
            print("Echec de la connection sftp (" + e + ")")
            exit()
        try:
            # print(sftp.listdir(path='.'))
            # print('--------')
            for entry in sftp.listdir_attr(path='.'):
                mode = entry.st_mode
                if S_ISDIR(mode):
                    # print(entry.filename + "/")
                    print("Goto Directory => " + entry.filename + "/")
                    explore_path(sftp, './'+entry.filename + "/")
                elif S_ISREG(mode):
                    print(' File found, go parsing : ' + entry.filename)
                    parse_file('.', entry.filename)
        except Exception as e:
            print(str(e))

    connect(transport, username, password)
    print('\nfichiers intéressants : ')
    for f in interesting_file:
        # print(f)
        typer.secho("Found interesting file: " +
                    f, fg=typer.colors.GREEN)
    raise typer.Exit()


@app.command()
def ftp(
        host: Optional[str] = typer.Option(...,
                                           "-h", help="Ip or hostname of target."),
        username: Optional[str] = typer.Option(..., "-u", help="Username"),
        password: Optional[str] = typer.Option(..., "-p", help="Password"),
        port: Optional[int] = typer.Option(21, "-P"),
        ext_file: Optional[Path] = typer.Option(None, "-w"),
        keywords_file: Optional[Path] = typer.Option(None, "-k")):

    interesting_file = []

    try:
        ftp = FTP(host)  # connexion à l'hôte
    except:
        print("Invalid host")
        exit()

    def filename_contains(filename, liste):
        liste = liste.split('\n')
        for text in liste:
            if text != "" and text in filename.lower():
                print("text : " + text + " , filename : " + filename.lower())
                return True
        return False

    def is_file(filename):
        try:
            return ftp.size(filename) is not None
        except:
            return False

    def parse_file(path, filename):
        if ext_file is None:
            typer.echo("No config file")
            raise typer.Abort()
        if ext_file.is_file():
            text = ext_file.read_text()
            file_ext = (filename.split('/')[-1]).split('.')[-1] or "empty"
            file_name = (filename.split('/')[-1]) or "empty"

            # if file_name == "test.txt":
            #     gFile = open("/home/msfadmin/vulnerable/test.txt", "r")
            #     buff = gFile.read()
            #     print(buff)
            #     gFile.close()

            # filter_by_ext(path, filename, IP, ext_file, keywords_file, conn)

        if (file_ext.lower() in text) or (filename_contains(file_name, text)):
            interesting_file.append(path)
            typer.secho("Found interesting file: " +
                        filename, fg=typer.colors.GREEN)
            # print(ext_file.read_text())

        elif ext_file.is_dir():
            typer.echo("Config is a directory, will use all its config files")
        elif not ext_file.exists():
            typer.echo("The config doesn't exist")

            line_counter = 0
            hits = 0
            file_obj = tempfile.NamedTemporaryFile()

            #    self.db.insertFileFinding(filename, share, IP, retrieveTimes(share,filename))

    def explore_path(path):
        try:
            if not is_file(path):
                print("Goto Directory => " + path)
                ftp.cwd(path)
            else:
                print(' File found, go parsing : ' + path)
                parse_file(path, path)
                return 1
        except Exception as e:
            print("error while changing directory : " + str(e))
        try:
            for p in ftp.nlst(path):
                explore_path(p)
        except Exception as e:
            print(str(e))

    def connect(ftp, username, password):
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
            # directories = ftp.retrlines('LIST -R') liste récursivement
            files = []
            try:
                files = ftp.nlst()
            except ftplib.error_perm as resp:
                if str(resp) == "550 No files found":
                    print("No files in this directory")
                else:
                    raise

            explore_path(ftp.pwd())
        except:
            print('error')

    connect(ftp, username, password)
    ftp.quit()
    print('\nFichiers intéressants : ')
    for f in interesting_file:
        typer.secho("Found interesting file: " +
                    f, fg=typer.colors.GREEN)


if __name__ == "__main__":
    app()
