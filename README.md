# Mita2 Tookit

Mita2 Tookit is a collection of Mitani-san personal command-line tools for MySQL.

## mita2-general-log-filter

```
$ mita2-general-log-filter --help
USAGE: mita2-general-log-filter [--user user] [--no-mask] [--help]
```

Filtering general log query executed by root user.
```
$ mita2-general-log-filter --user=root < /var/log/mysql-general.log
2019-03-17T14:19:14.673512Z	   20 Connect	root@localhost on  using Socket
2019-03-17T14:19:18.539830Z	   20 Query	select @@version_comment limit N
2019-03-17T14:19:27.603042Z	   20 Query	select * from mysql.user Where user = 'S'
2019-03-17T14:19:28.628762Z	   20 Quit
```

By default, mita2-general-log-filter masks values of SQL written in general log.
To disable masking, specify `--no-masking`.
```
$ mita2-general-log-filter --no-masking < /var/log/mysql-general.log
2019-03-17T14:19:14.673512Z	   20 Connect	root@localhost on  using Socket
2019-03-17T14:19:18.539830Z	   20 Query	select @@version_comment limit 1
2019-03-17T14:19:27.603042Z	   20 Query	select * from mysql.user Where user = 'root'
2019-03-17T14:19:28.628762Z	   20 Quit
```

