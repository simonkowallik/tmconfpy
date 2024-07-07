# tmconfpy

<p align="center">
<a href="https://github.com/simonkowallik/tmconfpy/actions/workflows/ci-pipeline.yaml">
    <img src="https://github.com/simonkowallik/tmconfpy/actions/workflows/ci-pipeline.yaml/badge.svg" alt="ci-pipeline">
</a>
<a href="https://codeclimate.com/github/simonkowallik/tmconfpy/test_coverage">
    <img src="https://api.codeclimate.com/v1/badges/3f404be294dceae16361/test_coverage" alt="test coverage">
</a>
<a href="https://hub.docker.com/r/simonkowallik/tmconfpy">
    <img src="https://img.shields.io/docker/image-size/simonkowallik/tmconfpy" alt="container image size">
</a>
<a href="https://github.com/simonkowallik/tmconfpy/releases">
    <img src="https://img.shields.io/github/v/release/simonkowallik/tmconfpy" alt="releases">
</a>
</p>

---

**tmconfpy** provides a simple parser (`tmconfpy` command) to serialize a tmconf file (eg. `/config/bigip.conf`) to JSON (or python `dict`). The produced JSON is printed to `STDOUT` or a specified output (`--output`) file. It is also usable as a python module for easy consumption in your own projects.

This project aims to be a minimalistic dependency free tool. It is based on [tmconfjs](https://github.com/simonkowallik/tmconfjs), it's parsing implementation leans heavily on the community project [F5 BIG-IP Automation Config Converter (BIG-IP ACC)](https://github.com/f5devcentral/f5-automation-config-converter/).

The TMOS configuration parser [f5-corkscrew](https://github.com/f5devcentral/f5-corkscrew) is a more sophisticated alternative with advanced functionality and active development.

Also checkout the jupyter notebook: [example/notebook.ipynb](./example/notebook.ipynb).

## Documentation by example

### Installation

```shell
pip3 install tmconfpy
```

### Command line usage

When installed globally, `tmconfpy` can be invoked as a command:

```shell
tmconfpy example/test.tmconf 2>/dev/null \
    | jq '."ltm profile client-ssl clientssl-secure"'
```

```json
{
  "app-service": "none",
  "cert": "/Common/default.crt",
  "cert-key-chain": {
    "default": {
      "cert": "/Common/default.crt",
      "key": "/Common/default.key"
    }
  },
  "chain": "none",
  "ciphers": "ecdhe:rsa:!sslv3:!rc4:!exp:!des",
  "defaults-from": "/Common/clientssl",
  "inherit-certkeychain": "true",
  "key": "/Common/default.key",
  "options": [
    "no-ssl",
    "no-tlsv1.3"
  ],
  "passphrase": "none",
  "renegotiation": "disabled"
}
```

Errors, warnings or any debug information is written to `STDERR`:

```shell
tmconfpy example/test.tmconf \
    >/dev/null 2> example/test.tmconf.log

cat example/test.tmconf.log
```

```shell
2024-06-30T18:39:16Z - WARNING - tmconfpy.parser - UNRECOGNIZED LINE for object 'sys software update': '     auto-check enabled'
2024-06-30T18:39:16Z - WARNING - tmconfpy.parser - UNRECOGNIZED LINE for object 'sys software update': '     auto-phonehome enabled'
2024-06-30T18:39:16Z - WARNING - tmconfpy.parser - UNRECOGNIZED LINE for object 'fatal-grace-time': '	time 500'
2024-06-30T18:39:16Z - WARNING - tmconfpy.parser - UNRECOGNIZED LINE for object 'fatal-grace-time': '	enabled yes'
```

Input is also accepted from `STDIN`:

```shell
cat example/imap.tmconf | tmconfpy
```

```json
{
    "ltm profile imap imap": {
        "activation-mode": "require"
    }
}
```

The `<file_path>` argument is preferred over `STDIN` however:

```shell
cat example/imap.tmconf | tmconfpy example/pop3.tmconf
```

```json
{
    "ltm profile pop3 pop3": {
        "activation-mode": "require"
    }
}
```

The output can be written to a specified file using `--output` or `-o` when `STDOUT` is not desired:

```shell
tmconfpy --output example/pop3.tmconf.json example/pop3.tmconf
cat example/pop3.tmconf.json
```

```json
{
    "ltm profile pop3 pop3": {
        "activation-mode": "require"
    }
}
```

tmconfpy supports multiple output formats of the parsed tmconf data, which can be specified via `--format`.

```shell
(cat example/imap.tmconf; echo; cat example/pop3.tmconf) | \
  tmconfpy --format jsonl
```

```json
{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}
{"path": "ltm profile pop3", "name": "pop3", "object": {"activation-mode": "require"}}
```

```shell
(cat example/imap.tmconf; echo; cat example/pop3.tmconf) | \
  tmconfpy --format tabular
```

```json
[
  ["ltm profile imap", "imap", {"activation-mode": "require"}],
  ["ltm profile pop3", "pop3", {"activation-mode": "require"}]
]
```

### Use as python module

```python
>>> from tmconfpy import Parser
>>> parsed = Parser('example/imap.tmconf', is_filepath=True)
>>> parsed.dict
{'ltm profile imap imap': {'activation-mode': 'require'}}
>>> tmconf = r"""
... ltm profile pop3 pop3 {
...     activation-mode require
... }
... ltm profile imap imap {
...     activation-mode require
... }
... """
>>> parsed = Parser(tmconf)
>>> parsed.json
'{"ltm profile pop3 pop3": {"activation-mode": "require"}, "ltm profile imap imap": {"activation-mode": "require"}}'
>>> parsed.tabular
[tabularTmconf(path='ltm profile pop3', name='pop3', object={'activation-mode': 'require'}), tabularTmconf(path='ltm profile imap', name='imap', object={'activation-mode': 'require'})]
>>> parsed.tabular_json
'[["ltm profile pop3", "pop3", {"activation-mode": "require"}], ["ltm profile imap", "imap", {"activation-mode": "require"}]]'
>>> parsed.jsonl
'{"path": "ltm profile pop3", "name": "pop3", "object": {"activation-mode": "require"}}\n{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}'
```

### Using the (optional) apiserver / container

Run the container, the API listens on port 8000 (http).

```shell
docker run --rm -p 8000:8000 simonkowallik/tmconfpy
```

The container is also available on [ghcr.io](https://github.com/simonkowallik/tmconfpy/pkgs/container/tmconfpy) as an alternative to docker hub.

```shell
docker run --rm -p 8000:8000 ghcr.io/simonkowallik/tmconfpy
```

The apiserver can be reached at [http://localhost:8000/](http://localhost:8000/) and offers two endpoints which are described by the OpenAPI specification.

API documentation can be reached at [/](http://localhost:8000/) and [/redoc](http://localhost:8000/redoc) for interactive use.

Parsing a single file by using POST, note `--data-binary` is required to avoid interpretation of the file content:

```shell
curl -X POST -s http://localhost:8000/parser/ \
  --data-binary @example/imap.tmconf
```

```json
{"ltm profile imap imap":{"activation-mode":"require"}}
```

Parsing multiple files via multipart form:

```shell
curl -X POST -s http://localhost:8000/fileparser/ \
  -F 'filename=@example/imap.tmconf' \
  -F 'filename=@example/pop3.tmconf'
```

```json
[
  {"filename":"imap.tmconf",
   "output":{"ltm profile imap imap":{"activation-mode":"require"}}
  },
  {"filename":"pop3.tmconf",
   "output":{"ltm profile pop3 pop3":{"activation-mode":"require"}}
  }
]
```

#### JSONL and tabular data

The `/parser/` api-endpoint also supports returning the parsed tmconf as JSONL or tabular data using the query parameter `?response_format=<format>`.

```shell
(cat example/imap.tmconf; echo; cat example/pop3.tmconf) | \
  curl -X POST -s http://localhost:8000/parser/?response_format=jsonl \
  --data-binary @-
```

```json
{"path": "ltm profile imap", "name": "imap", "object": {"activation-mode": "require"}}
{"path": "ltm profile pop3", "name": "pop3", "object": {"activation-mode": "require"}}
```

```shell
(cat example/imap.tmconf; echo; cat example/pop3.tmconf) | \
  curl -X POST -s http://localhost:8000/parser/?response_format=tabular \
  --data-binary @-
```

```json
[
  ["ltm profile imap","imap",{"activation-mode":"require"}],
  ["ltm profile pop3","pop3",{"activation-mode":"require"}]
]
```

#### Using the container as a command line tool

Use the `--entrypoint` argument with `tmconfpy` to invoke the tmconfpy tool instead of the apiserver (which is the default). Don't forget to pass `--interactive | -i` to the container.

```shell
cat example/imap.tmconf | docker run --rm --interactive --entrypoint tmconfpy simonkowallik/tmconfpy
```

```json
{
    "ltm profile imap imap": {
        "activation-mode": "require"
    }
}
```

**Note** that you can't use `--output | -o` to write the output to a file using the above method unless you mount a volume into the container.

## Disclaimer, Support, License

Please read and understand the [LICENSE](./LICENSE) first.

```
There is no support on this project.

It is maintained on best effort basis without any warranties.

For any software or components used in this project, read their own LICENSE and SUPPORT policies.

If you decide to use this project, you are solely responsible.
```
