### Odoo RESTful API(restful)

Basic understating of Odoo  is required in other to make good use of this module 

#### Access token request
An access token is required in other to be able to perform any operations and ths token once generated should alway be send a long side any subsequents request.
```python

```
### To delete acccess-token

```python
req = requests.delete('%s/api/auth/token'%base_url, data=data, headers=headers)
```
### [GET]
```python
req = requests.get('{}/api/sale.order/'.format(base_url), headers=headers,
                   data={'limit': 10, 'domain': []})
# ***Pass optional parameter like this ***
{
  'limit': 10, 'domain': "[('supplier','=',True),('parent_id','=', False)]",
  'order': 'name asc', 'offset': 10
}

print(req.content)

```
### [POST]
```python

**POST request**
```python
p = requests.post('%s/api/res.partner/'%base_url, headers=headers,
                  data=json.dumps({
    'name':'John',
    'country_id': 105,
    'child_ids': [{'name': 'Contact', 'type':'contact'},
                  {'name': 'Invoice', 'type':'invoice'}],
    'category_id': [{'id':9}, {'id': 10}]
    }
))
print(p.content)
```

**PUT Request**
```python
p = requests.put('http://theninnercicle.com.ng/api/res.partner/68', headers=headers,
                 data=json.dumps({
    'name':'John Doe',
    'country_id': 107,
    'category_id': [{'id': 10}]
    }
))
print(p.content)
```

**DELETE Request**
```python
p = requests.delete('http://theninnercicle.com.ng/api/res.partner/68', headers=headers)
print(p.content)
```
req = requests.get('{}/api/sale.order/'.format(base_url), headers=headers,data={'limit': 10, 'domain': []})