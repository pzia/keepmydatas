# keepmydatas
KMD is just a set of scripts designed to merge personal datas

If you try to merge multiple backups, multiples formats, multiples sources on and off-line, you needs some scripts to help.

Current formats are :
  * files : find duplicates
  * trees : remove empty folders, shrink trees (one file in a folder is very common after deduplication)
  * images : find duplicates and merge metadatas
  * mbox : deduplicate mails, auto-organize in datetree (/aaaa/mm)

Additional target formats could be :
  * vcf : universal vcard format, merging, ...
  * ical : merging multiple ical backups (ics format)
  * feeds : which format ? rss ? mbox (as thunderbird do ?)
  * bookmarks : using netscape universal format could be enough
