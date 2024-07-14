# tmconfpy and tmconfpy ansible collection

## Purpose

tmconfpy as well as the tmconfpy ansible collection aim to make BIG-IP configurations more accessible by serializing the tmconf format to python data structures.

This can be used to replace facts gathering in ansible, for ansible implementation specific purposes like checking for dependencies, or to query specific configuration information.

It also can help to audit configurations.

***NOTE:*** As the module copies configuration files from F5 BIG-IP devices, those configurations might contain sensitive data. Make sure YOU, as the implementor, *ensure* data security!

## Relevant configuration files

There are several relevant configuration files on F5 BIG-IP devices, here is a incomplete list:

- /config/bigip.conf
- /config/bigip_gtm.conf
- /config/bigip_base.conf
- /config/bigip_user.conf
- /config/partitions/\*/bigip\*.conf

## Data format examples

The tmconfpy ansible collection supports two formats to represent configurations, `object` (default) and `tabular`.

Type `object` basically means the configuration file is parsed as one big python dict. Of course a python dict can be serialized to JSON or YAML.

`object` example:

```json
{
    "module path object_name": {
        "description": "\"Object description\"",
        "property": "value"
    },
    "module path other_object_name": {
        "property": {
            "key": "value"
        }
    }
}
```

Type `tabular` returns a list of lists. It serializes each individual configuration object into a list with three entries `object_path` (`str`), `object_name` (`str`) and `object` (`dict`), each of the lists is then added to the main list of all objects.

`tabular` example:

```json
[
  [
   "module path",
   "object_name",
   { "description": "\"Object description\"", "property": "value" }
  ],
  [
   "module path",
   "other_object_name",
   { "property": { "key": "value" } }
  ]
]
```
