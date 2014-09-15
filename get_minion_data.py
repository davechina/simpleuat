#!/usr/bin/env python2.6
#

import salt.config
import salt.client
import salt.key
import redis
import datetime


def parse_config(config): 
	return salt.config.client_config(config)


def get_all_minions(opts):
	k = salt.key.Key(opts)
	all_keys = k.all_keys()
	return all_keys.get('minions')


def get_alive_minions():
	client = salt.client.LocalClient()
	ret = client.cmd('*', 'test.ping')
	return ret.keys()


def connect_redis(host, port=6379, db=0):
	return redis.StrictRedis(host, port=port, db=db)


def main():
	opts = parse_config('/etc/salt/master')
	all_minions = get_all_minions(opts)
	alive_minions = get_alive_minions()
	not_alive = list(set(all_minions).difference(set(alive_minions)))

	r = connect_redis('10.2.20.210')
	p = r.pipeline()

	name, key, value = 'aliveCount', '%s' % datetime.date.today(), len(alive_minions)
	p.hset(name, key, value)

	name1, key1, value1 = 'notaliveCount', '%s' % datetime.date.today(), len(not_alive)
	p.hset(name1, key1, value1)

	name2, key2, value2 = 'minionNoresponse', '%s' % datetime.date.today(), not_alive
	p.hset(name2, key2, value2)

	percent = '%.2f' % (len(alive_minions) / float(len(all_minions)) - 0.005)
	name3, key3, value3 = 'minionAlive', '%s' % datetime.date.today(), percent
	p.hset(name3, key3, value3)

	p.execute()
	# print len(all_minions)
	# print len(alive_minions)
	# print not_alive


if __name__ == '__main__':
	main()
