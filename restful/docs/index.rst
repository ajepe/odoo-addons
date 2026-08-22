Odoo RESTful API (restful)
~~~~~~~~~~~~~~~~~~~~~~~~~~

A generic REST API for Odoo. Every model of every installed module is
exposed through a simple, uniform HTTP interface. The implementation sits
on the existing Odoo ORM, so Odoo data structures and formats (domains,
x2many command lists, ...) still apply.

All examples use the ``sale.order`` model and the python ``requests``
library; any HTTP client works.

Access token request
^^^^^^^^^^^^^^^^^^^^

An access token is required in order to perform any operation, and the
token must be sent along with every subsequent request.

.. code:: python

    import requests

    base_url = 'http://localhost:8069'

    req = requests.get('{}/api/auth/token'.format(base_url),
                       params={'db': 'mydatabase',
                               'login': 'admin',
                               'password': 'admin'})
    content = req.json()

    # send the token on every request using the standard Bearer scheme
    headers = {
        'Authorization': 'Bearer {}'.format(content['access_token']),
        'Content-Type': 'application/json',
    }

.. note::

    The ``access-token`` header is also accepted for backward
    compatibility. Avoid the legacy ``access_token`` (underscore) header:
    HTTP servers and proxies silently drop headers containing underscores.

Requests run with the access rights and record rules of the user the
token belongs to.

Delete access token (logout)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    req = requests.delete('{}/api/auth/token'.format(base_url), headers=headers)

URL scheme
~~~~~~~~~~

::

    /api/<model>                  e.g. /api/sale.order
    /api/<model>/<id>             e.g. /api/sale.order/37
    /api/<model>/<id>/<action>    e.g. /api/sale.order/37/action_confirm

[GET] list records
~~~~~~~~~~~~~~~~~~

.. code:: python

    req = requests.get('{}/api/sale.order'.format(base_url), headers=headers,
                       params={'limit': 10,
                               'offset': 0,
                               'fields': 'name,partner_id,amount_total,state',
                               'domain': 'state:=:sale',
                               'order': 'id asc'})
    print(req.json())

Query parameters:

* ``limit``: maximum number of records to return
* ``offset``: number of records to skip
* ``fields``: comma-separated field names; omit to return all fields
* ``domain``: record filter as comma-separated ``field:operator:value``
  triplets, e.g. ``state:=:sale,amount_total:>:1000``
* ``order``: sort order, e.g. ``id asc``

[GET] one record
~~~~~~~~~~~~~~~~

.. code:: python

    req = requests.get('{}/api/sale.order/37'.format(base_url), headers=headers,
                       params={'fields': 'name,partner_id,amount_total,state'})
    print(req.json())

[POST] create a record
~~~~~~~~~~~~~~~~~~~~~~

Send the field values as a JSON body. One2many/Many2many fields take an
Odoo command list as a native JSON array, using the plain field name:

.. code:: python

    import json

    data = {
        'partner_id': 10,
        'order_line': [
            [0, 0, {'product_id': 1, 'product_uom_qty': 2, 'price_unit': 4000}],
            [0, 0, {'product_id': 2, 'product_uom_qty': 1, 'price_unit': 250}],
        ],
    }
    req = requests.post('{}/api/sale.order'.format(base_url), headers=headers,
                        params={'fields': 'name,amount_total'},
                        data=json.dumps(data))
    print(req.json())

``[0, 0, {...}]`` is the standard Odoo "create" command for x2many
fields; all Odoo command tuples are supported (``[1, id, {...}]`` update,
``[2, id]`` delete, ``[4, id]`` link, ``[6, 0, [ids]]`` replace, ...).

[PUT] update a record
~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    req = requests.put('{}/api/sale.order/37'.format(base_url), headers=headers,
                       data=json.dumps({'client_order_ref': 'PO-2024-118'}))
    print(req.json())

[PATCH] call a method on a record
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

PATCH invokes a model method (e.g. a button action) on a single record.
The method name goes in the URL; the request body is a JSON array of
positional arguments (``[]`` for none):

.. code:: python

    req = requests.patch('{}/api/sale.order/37/action_confirm'.format(base_url),
                         headers=headers, data=json.dumps([]))
    print(req.json())

This is equivalent to clicking the *Confirm* button on sale order 37.

[DELETE] delete a record
~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: python

    req = requests.delete('{}/api/sale.order/37'.format(base_url), headers=headers)
    print(req.json())

Responses
~~~~~~~~~

Successful responses always have the shape::

    {"count": 1, "data": ...}

Errors are JSON objects with an HTTP error status::

    {"type": "access_token", "message": "token seems to have expired or invalid"}

Status codes
~~~~~~~~~~~~

====  ===============  =========================================================
Code  Meaning          When
====  ===============  =========================================================
200   OK               Successful GET, PUT, PATCH, DELETE
201   Created          Successful POST
400   Bad Request      Missing credentials, malformed JSON body, invalid
                       id/arguments, Odoo validation errors
401   Unauthorized     Missing, expired or invalid access token, wrong
                       login/password
403   Forbidden        The token user is authenticated but lacks access
                       rights on the model
404   Not Found        Unknown model or record id, unknown method on record
====  ===============  =========================================================
