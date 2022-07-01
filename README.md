# CredsHarvester



Tool to browse, analyze and download all folders, files, available in network shares from several patterns (extensions, filename and regex) in an automated way. It supports SMB/Samba, FTP, SSH & SFTP

+ `git clone https://github.com/totaotata/CredsHarvester`
+ `cd CredsHarvester`
+ `pip install -r requirements.txt`

## How to use :

### Insert the file extensions you want in ext_file.txt
### Insert the keywords present in the files you want to find in keywords.txt


- ```python3 CredsHarvester.py --help```
- ```python3 CredsHarvester.py smb 192.168.1.2 -u username -p password -w ext_file.txt -k keywords.txt -P(optional port, default 139)```
- ```python3 CredsHarvester.py ftp 192.168.1.2 -u username -p password -w ext_file.txt -k keywords.txt -P(optional port, default 21)```
- ```python3 CredsHarvester.py sftp 192.168.1.2 -u username -p password -w ext_file.txt -k keywords.txt -P (optional port, default 22)```
- ```python3 CredsHarvester.py ssh 192.168.1.2 -u username -p password -w ext_file.txt -k keywords.txt -P(optional port, default 22)```


## To Do :
- [...] Add features to list all files and share with READ,WRITE access mode and export in .txt file with index line.
- [...] Export results to CSV
- [...] Add entrypoint option to start scan
- [?] Add possibilites to Stop scan and re-play on the same last point
- [] refacto with os.path lib (is_directory)
- [?] Create Class for arguments

- [] Insert result in SQLite database for better view and reserch
- [v2] Search with a list of login/password

## Done :
- [X] Search in file with regex
- [X] Improve error handling 

# Tips

- You can easily test this tool on the vulnerable metasploitable infrastructure or on the infrastructure of your choice ;)
