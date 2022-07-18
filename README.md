```

   _____              _                _    _                           _            
  / ____|            | |              | |  | |                         | |           
 | |     _ __ ___  __| |___   ______  | |__| | __ _ _ ____   _____  ___| |_ ___ _ __ 
 | |    | '__/ _ \/ _` / __| |______| |  __  |/ _` | '__\ \ / / _ \/ __| __/ _ \ '__|
 | |____| | |  __/ (_| \__ \          | |  | | (_| | |   \ V /  __/\__ \ ||  __/ |   
  \_____|_|  \___|\__,_|___/          |_|  |_|\__,_|_|    \_/ \___||___/\__\___|_|   

                                                                                   
```
                                                                                                        
                                                                                                        

# CredsHarvester - Why ?


Tool to browse, analyze and download all folders, files, available in network shares from several patterns (extensions, file name, regex and keywords in file contents) in an automated way.
It supports SMB/Samba, FTP, SSH and SFTP.

It can read files with the following extensions :


* .csv via python builtins
* .doc via antiword
* .docx via python-docx2txt
* .eml via python builtins
* .epub via ebooklib
* .gif via tesseract-ocr
* .jpg and .jpeg via tesseract-ocr
* .json via python builtins
* .html and .htm via beautifulsoup4
* .mp3 via sox, SpeechRecognition, and pocketsphinx
* .msg via msg-extractor
* .odt via python builtins
* .ogg via sox, SpeechRecognition, and pocketsphinx
* .pdf via pdftotext (default) or pdfminer* .six
* .png via tesseract-ocr
* .pptx via python-pptx
* .ps via ps2text
* .rtf via unrtf
* .tiff and .tif via tesseract-ocr
* .txt via python builtins
* .wav via SpeechRecognition and pocketsphinx
* .xlsx via xlrd
* .xls via xlrd




## Install :

+ `git clone https://github.com/totaotata/CredsHarvester`
+ `cd CredsHarvester`
+ `pip install -r requirements.txt`

## How to use :

- Add the file extensions you want in ext_file.txt
- Add keywords you want in keywords.txt
- Add regex you want in regex.txt
- ```python3 CredsHarvester.py --help```

## Usage :

- ```python3 CredsHarvester.py smb -h 192.168.1.2 -u 'username' -p 'password' -d 'domain.com' -w ext_file.txt -k keywords.txt -r regex.txt -P(optional, default is 445)```


### SFTP

- ```python3 CredsHarvester.py sftp -h 192.168.1.2 -u 'username' -p 'password' -d 'domain.com' -w ext_file.txt -k keywords.txt -r regex.txt -P (optional port, default is 22)```


### FTP :

- ```python3 CredsHarvester.py ftp -h 192.168.1.2 -u 'username' -p 'password' -d 'domain.com' -w ext_file.txt -k keywords.txt -r regex.txt -P(optional port, default is 21)```




## To Do :
- [ ] List all files and share with READ,WRITE access mode and export in .txt file with index line.
- [ ] Add possibilites to stop scan and re-start on the last point.
- [ ] Refact with os.path lib (is_directory)
- [ ] Create Class for arguments
- [ ] Insert result in SQLite database for better view and reserch ?
- [ ] Retrieve the content line when the keywords or regex are found
- [ ] Search with a list of login/password


## Done :
- [X] Add entrypoint option to start scan
- [X] Search in file with regex
- [X] Improve error handling 
- [X] Export results to CSV

## Tips

- You can easily test this tool on the vulnerable metasploitable infrastructure or on the infrastructure of your choice ;)
