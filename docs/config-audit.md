---
layout: default
title: Policy-as-Code - Config compliance
nav_enabled: true
nav_order: 4
---
{% raw %}

# Policy-as-Code - Config compliance

Policy-as-code (PaC) is an approach to defining, managing, and enforcing policies using code rather than manual processes. It involves writing policies in a high-level, machine-readable language that can be automatically enforced across IT infrastructure.

By implementing policy-as-code for F5 BIG-IP configurations, organizations can enhance their security posture, maintain consistent compliance across all BIG-IP estate, significantly reduces the risk of misconfigurations and ensure secure configuration practices.

Integrating policy checks into CI/CD pipelines allows for early detection of compliance issues, further strengthening the overall security posture and implement regular reporting.

Below are two examples where tmconfpy assists with policy-as-code.

## Using OPA conftest with rego to audit bigip.conf

Open Policy Agent (OPA) is an open-source, general-purpose policy engine that enables unified policy enforcement across various systems, using a declarative language called Rego for writing policies. Conftest, built on top of OPA, is a command-line tool that facilitates testing these policies against structured configuration data, making it easier to implement policy-as-code for various infrastructure components, which we will use to demonstrate policy-as-code for BIG-IP configuration.

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
FAIL - bigip.conf.json - main - Service /Common/vs_noncompliant_example.net with /Common/198.19.0.141:443 destination missing mandatory profile /Common/websecurity
FAIL - bigip.conf.json - main - Service /Common/vs_noncompliant_example.net-redirect80 with /Common/198.19.0.141:80 destination MUST NOT have pool attached
FAIL - bigip.conf.json - main - Service /Common/vs_noncompliant_example.net-redirect80 with /Common/198.19.0.141:80 destination missing mandatory rule /Common/redirect_to_https

20 tests, 17 passed, 0 warnings, 3 failures, 0 exceptions
```

Have a look at [conftest_policy_as_code.rego](https://github.com/simonkowallik/tmconfpy/blob/main/example/conftest_policy_as_code.rego) for the policy definitions.

## tmconfpy with pytest for auditing configuration compliance ("policy-as-code")

Pytest, a popular Python testing framework, can be leveraged for implementing policy-as-code by writing test functions that reflect policies as code and test configuration data against them.

Checkout the example in [pytest_policy_as_code.py](https://github.com/simonkowallik/tmconfpy/blob/main/example/pytest_policy_as_code.py), see below for example output based on `bigip.conf`.

```shell
pytest pytest_policy_as_code.py --tb=line -v
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

{% endraw %}
