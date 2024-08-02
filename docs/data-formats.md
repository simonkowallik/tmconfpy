---
layout: default
title: Data formats
nav_enabled: true
nav_order: 2
---
# tmconfpy data formats

## Relevant configuration files

There are several relevant configuration files on F5 BIG-IP devices, here is a incomplete list:

- /config/bigip.conf
- /config/bigip_gtm.conf
- /config/bigip_base.conf
- /config/bigip_user.conf
- /config/partitions/\*/bigip\*.conf

## example configuration data

The tmconfpy ansible collection supports multiple formats to represent configuration data, see below.

The example tmconf data (imaginary objects):

```python
import tmconfpy
parsed_tmconf = tmconfpy.Parser(r"""
module path name {
    description "Object description"
    property value
    list { 2 a c b 1 }
    obj {
        a_key value
        b_key value2
    }
},
module path another_name {
    property value
}""")
```

### object format

The configuration file is parsed as one big python dict. Of course a python dict can be serialized to JSON or YAML. JSON is built-in (YAML is not).

```python
>>> parsed_tmconf.dict
{
 'module path name': {'description': '"Object description"',
                      'property': 'value',
                      'list': ['2', 'a', 'c', 'b', '1'],
                      'obj': {'a_key': 'value', 'b_key': 'value2'}},
 'module path another_name': {'property': 'value'}
}
```

`parsed_tmconf.json`:

```json
{
  "module path name": {
    "description": "\"Object description\"",
    "property": "value",
    "list": ["2", "a", "c", "b", "1"],
    "obj": { "a_key": "value", "b_key": "value2" }
  },
  "module path another_name": { "property": "value" }
}
```

### tabular format

Tabular format serializes each individual configuration object into a list with three elements; `path` (`str`), `name` (`str`) and `object` (`dict`). Each of the lists is then added to the main list of all objects.

So `path`, `name` and `object` are the columns and each entry in the configuration file will be a row.

```python
>>> parsed_tmconf.tabular
[
    tabularTmconf(path='module path', name='name', object={'description': '"Object description"', 'property': 'value', 'list': ['2', 'a', 'c', 'b', '1'], 'obj': {'a_key': 'value', 'b_key': 'value2'}}),
    tabularTmconf(path='module path', name='another_name', object={'property': 'value'})
 ]
```

`parsed_tmconf.tabular_json`:

```json
[
  [
    "module path", "name", {
          "description": "\"Object description\"",
          "property": "value",
          "list": ["2", "a", "c", "b", "1"],
          "obj": { "a_key": "value", "b_key": "value2" }
        }
  ],
  [ "module path", "another_name", { "property": "value" } ]
]
```

### tabular key value format

Like the tabular format the tabular key value format (tabular_kv) formats the configuration data in a list of entries. In contrast to the tabular format, each entry is not a list but a key value dict / object. While this is more inefficient than the tabular format (namedtuples vs. dict, JSON is smaller), in many use-cases it is simpler. For example when using jmespath to query the data (an important use-case for ansible).

```python
>>> parsed_tmconf.tabular_kv
[
  {'path': 'module path', 'name': 'name',
   'object': {
          'description': '"Object description"',
          'property': 'value',
          'list': ['2', 'a', 'c', 'b', '1'],
          'obj': {'a_key': 'value', 'b_key': 'value2'}
    }
  },
  {'path': 'module path', 'name': 'another_name', 'object': {'property': 'value'}}
]
```

`parsed_tmconf.tabular_json_kv`:

```json
[
  {
    "path": "module path",
    "name": "name",
    "object": {
      "description": "\"Object description\"",
      "property": "value",
      "list": ["2", "a", "c", "b", "1"],
      "obj": { "a_key": "value", "b_key": "value2" }
    }
  },
  {
    "path": "module path",
    "name": "another_name",
    "object": { "property": "value" }
  }
]
```
