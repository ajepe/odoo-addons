Odoo RESTful API(restful)
~~~~~~~~~~~~~~~~~~~~~~~~~

In other to use this module, a basic understating of Odoo RPC interface
is required(though not that neccessary) especially when dealing with
Many2many and One2many relationship. The implementation sits on the
existing Odoo RPC features, data structures and format when creating or
delecting Odoo's records are still applicable. I will be demostrating
the usage using python request library.

Access token request
^^^^^^^^^^^^^^^^^^^^

An access token is required in other to be able to perform any
operations and ths token once generated should alway be send a long side
any subsequents request.

.. code:: python

    import requests

    headers = {
        'charset':'utf-8'
    }

    data = {
        'login': 'admin',
        'password': 'admin',
        'db': 'demo_db'
    }
    base_url = 'http://theninnercicle.com.ng'

    req = requests.post('{}/api/auth/token'.format(base_url), data=data, headers=headers)
    content = req.json()

    headers['access-token'] = content['access_token'] # add the access token to the header
    print(headers)

To delete acccess-token
~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    req = requests.delete('{}/api/auth/token'.format(base_url), params=query, headers=headers)

[GET]
~~~~~

.. code:: python

    import requests

    headers = {
        'charset': 'utf-8',
        'access-token': 'access_token'
    }
    model = 'res.partner'

    # You can get object by its id
    id = 100
    req = requests.get('{}/api/{}/{}'.format(base_url, model, id), headers=headers)
    print(req.json())

    # You can make queries
    headers['content-type'] = 'application/x-www-form-urlencoded'
    query = {
        'domain': "[('supplier','=',True),('parent_id','=', False)]",
        'order': ['name asc', 'id'], # or 'name asc, id'
        'limit': 10,
        'offset': 0,
        'fields': "['name', 'supplier', 'parent_id']"
    }

    # You can ommit unnessesary query options
    query = {
        'domain': "[('supplier','=',True),('parent_id','=', False)]",
        'limit': 10
    }

    # You can also use JSON-like domains
    query = {
        'domain': "{'id':100, 'parent_id!':true}",
        'limit': 10
    }
    req = requests.get('{}/api/{}/'.format(base_url, model), headers=headers, params=query)
    print(req.json())

[POST]
~~~~~~

.. code:: python

    model = 'res.partner'
    data = {
        'name': 'Babatope Ajepe',
        'country_id': 105,
        'child_ids': [
            {
                'name': 'Contact',
                'type': 'contact'
            },
            {
                'name': 'Invoice',
                'type': 'invoice'
            }
        ],
        'category_id': [{'id': 9}, {'id': 10}]
    }
    req = requests.post('{}/api/{}/'.format(base_url, model), headers=headers, data=data)
    print(req.json())

[PUT]
~~~~~~

.. code:: python

    model = 'res.partner'
    id = 100
    data = {
        'name': 'Babatope Ajepe',
        'country_id': 103,
        'category_id': [{'id': 9}]
    }
    req = requests.put('{}/api/{}/{}'.format(base_url, model, id), headers=headers, data=data)
    print(req.json())

[DELETE]

.. code:: python

    model = 'res.partner'
    id = 100
    req = requests.delete('{}/api/{}/{}'.format(base_url, model, id), headers=headers)
    print(req.status_code)

