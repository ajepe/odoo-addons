# Odoo Redis Session Storage
------------------------------

This module allows you to use a Redis database to manage sessions, instead of the default Odoo filesystem implementation.

Redis is an open source, in-memory data structure store, used as a database, cache and message broker.

This module is needed when you have multiple instance of Odoo application server running behind a load balancing application.

There will be need to share user session information.

You need to install and to start a Redis server to use this module.
Documentation is available on `Redis website`_.

You need to install package **redis**
```
    pip3 install redis # http://redis.io/topics/quickstart
```

### Usage or Configuation
addd and set these following parameter in your configuration file
```bash
session_store = redis
redis://username:password@ipaddress:6379/0 
```
* The username is optional but a place holder should be set as shown above
* Replace the password with your redis auth password
* ipaddress with the redis server address e.g

```
e.g
//.odoorc as the config file name or your name of choice.

session_store = redis
redis=redis://username:avlpynVhwvBa34x10NNINZiMRW2C8iJO@redis-13852.c14.us-east-1-2.ec2.cloud.redislabs.com:13852/0`
```
