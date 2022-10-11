# Fetch the original English translation file and build a new one,
# either derived from an existing one or built from the English file.

import csv
from os.path import exists
import re
import requests
import shutil
import sys
import time


if len(sys.argv) > 1:
  print("Rebuilding " + sys.argv[1] + ".csv …")
  if exists(sys.argv[1] + ".csv"):
    file_targetLang = open(sys.argv[1] + ".csv", "r")
    content_targetLang = {}
    csv_targetLang = csv.reader(file_targetLang)
    for row in csv_targetLang:
      if not 2 in row:
        row.append("")
      content_targetLang[row[0]] = {"value": row[1], "comment": row[2]}
    file_targetLang.close()

    # Create a backup with timestamp.
    now = time.localtime(time.time())
    file_backup_path = sys.argv[1] + "_backup_" + str(now.tm_year) + "-" + str(now.tm_mon) + "-" + str(now.tm_mday) + "-" + str(now.tm_hour) + "-" + str(now.tm_min) + "-" + str(now.tm_sec) + ".csv"
    shutil.copyfile(sys.argv[1] + ".csv", file_backup_path)
  
  else:
    file_targetLang = open(sys.argv[1] + ".csv", "w")
    content_targetLang = []
    file_targetLang.close()

  file_english = requests.get("https://docs.google.com/spreadsheets/d/1iiaORk6Ma5c2DpijK3oFs08fdk9PAe7QsCoiiBzdEUU/export?format=csv&id=1iiaORk6Ma5c2DpijK3oFs08fdk9PAe7QsCoiiBzdEUU&gid=0")
  
  if file_english.ok:
    content_english = file_english.content.decode('utf-8').split("\r\n")
    
    # Save the first entry (explaination for the list), sort the rest and prepend the first one again.
    firstEntry = content_english[0]
    del content_english[0]
    content_english.sort()
    content_english.insert(0, firstEntry)
  
    string_targetLang = firstEntry + "\n"
    
    # Skip the first line (explaination).
    for i in range(1, len(content_english)):
      # Skip empty lines.
      key = re.findall("^[^,]+", content_english[i])
      if len(key) > 0:
        key = key[0]
      else:
        continue
         
      if key in content_targetLang:
        string_targetLang = string_targetLang + key + ",\"" + content_targetLang[key]['value'] + "\",\"" + content_targetLang[key]['comment'] + "\"\n"
      else:
        string_targetLang = string_targetLang + content_english[i] + ",\"TO DO! NO TRANSLATION YET\"" + "\n"
        
    file_targetLang = open(sys.argv[1] + ".csv", "w")
    file_targetLang.write(string_targetLang)
    file_targetLang.close()

    print("Done.")

else:
  print("Please provide a language name to rebuild.")
  exit(1)
