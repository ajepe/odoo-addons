# Odoo RESTful API

A generic REST API for Odoo. Every model of every installed module is exposed
through a simple, uniform HTTP interface — no per-model code required.

All examples below use the `sale.order` model and the Python `requests`
library, but any HTTP client works.

Base URL used in the examples: `http://localhost:8069`

## Authentication

An access token is required for all requests except the token endpoint itself.

### Get a token

The following fields are needed for token generation:

1. `db`: the database the user is connecting to
2. `login`: a valid user login or email
3. `password`: the account password

```python
import requests

url = "http://localhost:8069/api/auth/token"
params = {"db": "mydatabase", "login": "admin", "password": "admin"}

response = requests.get(url, params=params)
print(response.json())
```

Token response:

```json
{
  "uid": 2,
  "user_context": {"lang": "en_US", "tz": "Europe/Brussels", "uid": 2},
  "company_id": 1,
  "company_ids": [1],
  "partner_id": 3,
  "access_token": "access_token_bb4545413125847104b02a4e9a4aa8088a90903d",
  "company_name": "YourCompany",
  "currency": "USD",
  "country": "United States",
  "contact_address": "YourCompany\n215 Vine St\n\nScranton PA 18503\nUnited States"
}
```

### Send the token

Send the token on every request using the standard `Authorization: Bearer`
scheme:

```python
headers = {
    "Authorization": "Bearer access_token_bb4545413125847104b02a4e9a4aa8088a90903d",
    "Content-Type": "application/json",
}
```

> The `access-token` header is also accepted for backward compatibility.
> Avoid the legacy `access_token` (underscore) header: HTTP servers and
> proxies silently drop headers containing underscores.

### Revoke a token (logout)

```python
response = requests.delete("http://localhost:8069/api/auth/token", headers=headers)
print(response.json())
# {"count": 1, "data": [{"message": "access token ... successfully deleted", "delete": true}]}
```

## Permissions

Requests run with the access rights and record rules of the user the token
belongs to. If a request is rejected, check that user's permissions in Odoo.

## URL scheme

```
/api/<model>                  e.g. /api/sale.order
/api/<model>/<id>             e.g. /api/sale.order/37
/api/<model>/<id>/<action>    e.g. /api/sale.order/37/action_confirm
```

## CRUD operations on sale.order

### GET — list records

```python
import requests

url = "http://localhost:8069/api/sale.order"
params = {
    "limit": 10,
    "offset": 0,
    "fields": "name,partner_id,amount_total,state",
    "domain": "state:=:sale",
    "order": "id asc",
}

response = requests.get(url, params=params, headers=headers)
print(response.json())
```

Query parameters:

* `limit`: maximum number of records to return
* `offset`: number of records to skip
* `fields`: comma-separated field names; omit to return all fields
* `domain`: record filter as comma-separated `field:operator:value` triplets,
  e.g. `state:=:sale,amount_total:>:1000`
* `order`: sort order, e.g. `id asc`

Response:

```json
{
  "count": 2,
  "data": [
    {"id": 36, "name": "SO036", "partner_id": [10, "Gemini Furniture"], "amount_total": 1025.0, "state": "sale"},
    {"id": 37, "name": "SO037", "partner_id": [11, "Azure Interior"], "amount_total": 2400.0, "state": "sale"}
  ]
}
```

### GET — one record

```python
response = requests.get(
    "http://localhost:8069/api/sale.order/37",
    params={"fields": "name,partner_id,amount_total,state"},
    headers=headers,
)
print(response.json())
```

### POST — create a record

Send the field values as a JSON body. One2many/Many2many fields take an
Odoo command list as a native JSON array, using the plain field name:

```python
import json
import requests

url = "http://localhost:8069/api/sale.order"
data = {
    "partner_id": 10,
    "order_line": [
        [0, 0, {"product_id": 1, "product_uom_qty": 2, "price_unit": 4000}],
        [0, 0, {"product_id": 2, "product_uom_qty": 1, "price_unit": 250}],
    ],
}

response = requests.post(url, params={"fields": "name,amount_total"},
                         data=json.dumps(data), headers=headers)
print(response.json())
```

`[0, 0, {...}]` is the standard Odoo "create" command for x2many fields; all
Odoo command tuples are supported (`[1, id, {...}]` update, `[2, id]` delete,
`[4, id]` link, `[6, 0, [ids]]` replace, ...).

### PUT — update a record

```python
response = requests.put(
    "http://localhost:8069/api/sale.order/37",
    data=json.dumps({"client_order_ref": "PO-2024-118"}),
    headers=headers,
)
print(response.json())
```

### PATCH — call a method on a record

PATCH invokes a model method (e.g. a button action) on a single record. The
method name goes in the URL; the request body is a python-literal list of
positional arguments (`[]` for none):

```python
response = requests.patch(
    "http://localhost:8069/api/sale.order/37/action_confirm",
    data="[]",
    headers=headers,
)
print(response.json())
```

This is equivalent to clicking the *Confirm* button on sale order 37.

### DELETE — delete a record

```python
response = requests.delete("http://localhost:8069/api/sale.order/37", headers=headers)
print(response.json())
# {"count": 1, "data": "record 37 has been successfully deleted"}
```

## Responses

Successful responses always have the shape:

```json
{"count": 1, "data": ...}
```

Errors are JSON objects with an HTTP error status:

```json
{"type": "access_token", "message": "token seems to have expired or invalid"}
```

### Status codes

| Code | Meaning | When |
|---|---|---|
| 200 | OK | Successful GET, PUT, PATCH, DELETE |
| 201 | Created | Successful POST |
| 400 | Bad Request | Missing credentials, malformed JSON body, invalid id/arguments, Odoo validation errors |
| 401 | Unauthorized | Missing, expired or invalid access token, wrong login/password |
| 403 | Forbidden | The token user is authenticated but lacks access rights on the model |
| 404 | Not Found | Unknown model or record id, unknown method on record |
