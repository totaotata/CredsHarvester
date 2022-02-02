# CredsHarvester


Tool to browse, analyze and download all folders, files, available in network shares from several patterns (extensions, filename and regex) in an automated way. It supports SMB/Samba, FTP, SSH & SFTP

+ `git clone https://github.com/totaotata/CredsHarvester`
+ `cd CredsHarvester`
+ `pip install -r requirements.txt`

## How to use :


- python3 CredsHarvester --help
- python3 CredsHarvester smb 192.168.1.2 -u username -pwd password -p(optional port, default 139)
- python3 CredsHarvester ftp 192.168.1.2 -u username -pwd password -p(optional port, default 21)
- python3 CredsHarvester sftp 192.168.1.2 -u username -pwd password -p (optional port, default 22)
- python3 CredsHarvester ssh 192.168.1.2 -u username -pwd password -p(optional port, default 22)


## To Do :
- add wordList comparation
- Handle error


# Tips

- you can easily test this tool on the vulnerable metasploitable infrastructure or on the infrastructure of your choice ;)