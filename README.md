# Mita2 Tookit

Mita2 Tookit is a collection of Mitani-san personal command-line tools for MySQL.

## mita2-general-log-filter

```
$ mita2-general-log-filter.py --help
USAGE: mita2-general-log-filter [--user user] [--no-mask] [--command Command] [--help]
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

## mita2-binlog-mask

```
$ mita2-binlog-mask.py --help
USAGE: mysqlbinlog -vv --base64-output=DECODE-ROWS binlog-file | mita2-general-log-filter.py [--preserve=schema.table.column_pos,schema.table.column_pos...]

This script masks values in your decoded binary log.
Binlog must be ROW formatted. Check your binlog_format is ROW.
```

```
$ sudo mysqlbinlog -vv --base64-output=DECODE-ROWS   /var/lib/mysql/mysqld-bin.000002 | ./mita2-binlog-mask.py
<snip>
### INSERT INTO `test`.`t`
### SET
###   @1=6280441344041169268 /* LONGINT meta=0 nullable=0 is_null=0 */
###   @2='EFIA7R01TBPE9ADWOYH' /* VARSTRING(255) meta=255 nullable=0 is_null=0 */
###   @3=2140268343 /* INT meta=0 nullable=1 is_null=0 */
###   @4='2020-12-25 21:17:29' /* DATETIME(0) meta=0 nullable=1 is_null=0 */
# at 2411
#201213  7:20:10 server id 1  end_log_pos 2442 CRC32 0xa7ef99a3 	Xid = 43
COMMIT/*!*/;
# at 2442
#201213  8:34:32 server id 1  end_log_pos 2465 CRC32 0x2bac8b8d 	Stop
SET @@SESSION.GTID_NEXT= 'AUTOMATIC' /* added by mysqlbinlog */ /*!*/;
DELIMITER ;
# End of log file
/*!50003 SET COMPLETION_TYPE=@OLD_COMPLETION_TYPE*/;
/*!50530 SET @@SESSION.PSEUDO_SLAVE_MODE=0*/;
```

To disable masking for certain column, set `--preserve` option.
eg) disable masking for first column of test.t table.
```
$ sudo mysqlbinlog -vv --base64-output=DECODE-ROWS   /var/lib/mysql/mysqld-bin.000002 | ./mita2-binlog-mask.py --preserve=test.t.1
<snip>
### INSERT INTO `test`.`t`
### SET
###   @1=4 /* LONGINT meta=0 nullable=0 is_null=0 */
###   @2='Z7JO3ETZEXBV7I9747F' /* VARSTRING(255) meta=255 nullable=0 is_null=0 */
###   @3=4119513598 /* INT meta=0 nullable=1 is_null=0 */
###   @4='2020-12-18 23:18:09' /* DATETIME(0) meta=0 nullable=1 is_null=0 */
# at 2411
#201213  7:20:10 server id 1  end_log_pos 2442 CRC32 0xa7ef99a3 	Xid = 43
COMMIT/*!*/;
# at 2442
#201213  8:34:32 server id 1  end_log_pos 2465 CRC32 0x2bac8b8d 	Stop
SET @@SESSION.GTID_NEXT= 'AUTOMATIC' /* added by mysqlbinlog */ /*!*/;
DELIMITER ;
# End of log file
/*!50003 SET COMPLETION_TYPE=@OLD_COMPLETION_TYPE*/;
/*!50530 SET @@SESSION.PSEUDO_SLAVE_MODE=0*/;
```
