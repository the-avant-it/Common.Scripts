Example:

export-cloudflare-records.py

```
qtu100@qtu100:~/dev/avant/MAIN/1-COMMON/OTHER/common.scripts/dns-import-export$ ./export-cloudflare-records.py 
Input Cloudflare API SECRET_KEY
Token is valid!
0) hostname SECRET_KEY
1) hostname SECRET_KEY
Enter space separated numbers of zones you want to export. Enter -1 to export all: -1
All zones selected
Exporting hostname SECRET_KEY...
Exporting 81 records
81 records exported!
hostname exported to hostname.yaml
Exporting hostname SECRET_KEY...
Exporting 220 records
100 records exported!
100 records exported!
20 records exported!
hostname exported to hostname.yaml
```

import-dns-records-to-yandex.py

```
qtu100@qtu100:~/dev/avant/MAIN/1-COMMON/OTHER/common.scripts/dns-import-export$ ./import-dns-records-to-yandex.py 
Note, you have to install yandex cli!
Input path to exported records: hostname.yaml
The file appears to be valid!
Enter yandex DNS zone id: dnsfnefqrup9hkau6p1j
Command: yc dns zone add-records dnsfnefqrup9hkau6p1j --record="alb-int.hostname A 172.20.52.33" --format=json returned: {
  "additions": [
    {
      "name": "alb-int.hostname.hostname.",
      "type": "A",
      "ttl": "600",
...
```