# example

## jupyter notebook

Have a look at the jupyter notebook [notebook.ipynb](./notebook.ipynb) for examples on how to work with tmconfpy interactively in python.

## Using OPA conftest with rego to audit bigip.conf

Install conftest:

```shell
curl -sLo - \
    https://github.com/open-policy-agent/conftest/releases/download/v0.56.0/conftest_0.56.0_Linux_x86_64.tar.gz \
    | tar xzp conftest

```

Convert bigip.conf to JSON:

```shell
tmconfpy ./bigip.conf --format tabular_kv -o ./bigip.conf.json 
```

Run conftest specifying the rego policy:

```shell
./conftest test -p conftest_policy_as_code.rego bigip.conf.json 
```

```shell
FAIL - bigip.conf.json - main - Service /Common/vs_noncompliant_example.net with /Common/198.19.0.141:443 destination missing mandatory profile /Common/websecurity
FAIL - bigip.conf.json - main - Service /Common/vs_noncompliant_example.net-redirect80 with /Common/198.19.0.141:80 destination MUST NOT have pool attached
FAIL - bigip.conf.json - main - Service /Common/vs_noncompliant_example.net-redirect80 with /Common/198.19.0.141:80 destination missing mandatory rule /Common/redirect_to_https

20 tests, 17 passed, 0 warnings, 3 failures, 0 exceptions
```

## tmconfpy with pytest for auditing configuration compliance ("policy-as-code")

To use tmconfpy with pytest for configuration compliance auditing, you can write test cases that parse configuration files using tmconfpy and assert that the parsed configurations meet your compliance requirements. By integrating tmconfpy with pytest, you can automate the validation of configuration files and ensure they adhere to predefined standards.

Checkout the example in [pytest_policy_as_code.py](./pytest_policy_as_code.py), see below for example output based on [bigip.conf](./bigip.conf).

```shell
pytest pytest_policy_as_code.py --tb=line -v
```

```shell
===================================================================================================================================== test session starts ======================================================================================================================================
platform linux -- Python 3.10.12, pytest-8.3.3, pluggy-1.5.0 -- tmconfpy/.venv/bin/python
cachedir: .pytest_cache
rootdir: tmconfpy
configfile: pyproject.toml
plugins: anyio-4.6.2.post1, mock-3.14.0, cov-6.0.0
collected 8 items

pytest_policy_as_code.py::Test_audit_virtuals::test_for_mandatory_profiles[:443-/Common/websecurity-exact] FAILED
pytest_policy_as_code.py::Test_audit_virtuals::test_for_mandatory_profiles[:443-/Common/clientssl-startswith] PASSED
pytest_policy_as_code.py::Test_audit_virtuals::test_for_mandatory_profiles[:443-/Common/serverssl-startswith] PASSED
pytest_policy_as_code.py::Test_audit_virtuals::test_absence_of_pool_on_http_virtuals[:80-pool] FAILED
pytest_policy_as_code.py::Test_audit_virtuals::test_redirect_rule_on_http_virtuals[:80-/Common/redirect_to_https] FAILED
pytest_policy_as_code.py::Test_audit_virtuals::test_allowed_virtual_server_ports PASSED
pytest_policy_as_code.py::Test_audit_clientssl::test_chain_is_set PASSED
pytest_policy_as_code.py::Test_audit_clientssl::test_defaults_from_secure PASSED

=========================================================================================================================================== FAILURES ===========================================================================================================================================
tmconfpy/example/pytest_policy_as_code.py:45: AssertionError: Service /Common/vs_noncompliant_example.net with :443 destination missing /Common/websecurity profile
tmconfpy/example/pytest_policy_as_code.py:63: AssertionError: Service /Common/vs_noncompliant_example.net-redirect80 with :80 destination should not have attribute pool
tmconfpy/example/pytest_policy_as_code.py:77: AssertionError: Service /Common/vs_noncompliant_example.net-redirect80 with :80 destination missing /Common/redirect_to_https rule
=================================================================================================================================== short test summary info ====================================================================================================================================
FAILED pytest_policy_as_code.py::Test_audit_virtuals::test_for_mandatory_profiles[:443-/Common/websecurity-exact] - AssertionError: Service /Common/vs_noncompliant_example.net with :443 destination missing /Common/websecurity profile
FAILED pytest_policy_as_code.py::Test_audit_virtuals::test_absence_of_pool_on_http_virtuals[:80-pool] - AssertionError: Service /Common/vs_noncompliant_example.net-redirect80 with :80 destination should not have attribute pool
FAILED pytest_policy_as_code.py::Test_audit_virtuals::test_redirect_rule_on_http_virtuals[:80-/Common/redirect_to_https] - AssertionError: Service /Common/vs_noncompliant_example.net-redirect80 with :80 destination missing /Common/redirect_to_https rule
================================================================================================================================= 3 failed, 5 passed in 0.02s ==================================================================================================================================

```
