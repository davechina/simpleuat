#!/usr/bin/env python2.7
#

import MySQLdb
import datetime


class GetZabbixData(object):
    def __init__(self, host, port, user, password, db):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.db = db

    def get_zbx_stat(self, sql):
        try:
            conn = MySQLdb.connect(host=self.host, user=self.user, passwd=self.password, port=self.port, db=self.db)
        except:
            print 'connect failed.'
            exit()

        cur = conn.cursor()
        cur.execute(sql)
        data = cur.fetchall()

        return data


if __name__ == '__main__':
    user = r'uapp_zbxreader'
    password = r'wY4slvrnHcc7@tw'
    host = r'10.2.22.19'
    port = 55666
    db = 'zabbix'
    zbx = GetZabbixData(host, port, user, password, db)

    
    icmp_sql = r"select h.host,fn_getlastvalue(i.itemid,UNIX_TIMESTAMP()-delay-300) as value from items i inner join hosts h on i.hostid=h.hostid where key_ = 'icmpping';"
    icmp_stat = zbx.get_zbx_stat(icmp_sql)
    print dict(list(icmp_stat))


    # this_hour = datetime.datetime.now().replace(minute=0, second=0, microsecond=0).isoformat().replace('T', ' ')
    # last_hour = (datetime.datetime.now() + datetime.timedelta(hours = -1)).replace(minute=0, second=0, microsecond=0).isoformat().replace('T', ' ')


    # mem_sql = r"select h.host,key_,avg(value) as value_avg from items i inner join hosts h on i.hostid=h.hostid inner join history his on i.itemid=his.itemid where key_ = 'vm.memory.size[pavailable]' and clock>=UNIX_TIMESTAMP('%s') and clock<UNIX_TIMESTAMP('%s') group by h.host,key_;" %((datetime.datetime.now()+datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00'), datetime.datetime.now().strftime('%Y-%m-%d %H:00:00'))
    # mem_stat = zbx.get_zbx_stat(mem_sql)
    # print dict(list(mem_stat))

    # ser_sql = r"select host,max(if((key_= 'vm.memory.size[pavailable]'),value_avg,NULL)) AS vm,max(if((key_= 'system.swap.size[,pfree]'),value_avg,NULL)) AS swap,max(if((key_= 'system.cpu.load'),value_avg,NULL)) AS cpu from (select h.host,key_,avg(value) as value_avg from items i inner join hosts h on i.hostid=h.hostid inner join history his on i.itemid=his.itemid where key_ in ('vm.memory.size[pavailable]','system.swap.size[,pfree]','system.cpu.load') and clock>=UNIX_TIMESTAMP('%s') and clock<=UNIX_TIMESTAMP('%s') group by h.host,key_)tbl group by host;" % ((datetime.datetime.now()+datetime.timedelta(hours=-1)).strftime('%Y-%m-%d %H:00:00'), datetime.datetime.now().strftime('%Y-%m-%d %H:00:00'))
    # ser_stat = zbx.get_zbx_stat(ser_sql)
    # print ser_stat

