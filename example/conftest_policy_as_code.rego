# OPA rego - policy as code example

package main

import future.keywords.in

deny[msg] {
    mandatory_profiles := ["/Common/serverssl-secure", "/Common/websecurity"]
    input.path == "ltm virtual"
    destination := input.object.destination
    port := split(split(destination, "%")[0], ":")[1]
    port == "443"
    some mandatory_profile in mandatory_profiles
    not input.object.profiles[mandatory_profile]
    msg := sprintf("Service %s with %s destination missing mandatory profile %s", [input.name, input.object.destination, mandatory_profile])
}

deny[msg] {
    mandatory_profile := "/Common/clientssl"
    input.path == "ltm virtual"
    destination := input.object.destination
    port := split(split(destination, "%")[0], ":")[1]
    port == "443"
    profiles := object.keys(input.object.profiles)
    not strings.any_prefix_match(profiles, mandatory_profile)
    msg := sprintf("Service %s with %s destination missing mandatory profile %s", [input.name, input.object.destination, mandatory_profile])
}

deny[msg] {
    destination := input.object.destination
    input.path == "ltm virtual"
    port := split(split(destination, "%")[0], ":")[1]
    port == "80"
    input.object.pool != null
    msg := sprintf("Service %s with %s destination MUST NOT have pool attached", [input.name, destination])
}

deny[msg] {
    mandatory_rule := "/Common/redirect_to_https"
    destination := input.object.destination
    input.path == "ltm virtual"
    port := split(split(destination, "%")[0], ":")[1]
    port == "80"
    not input.object.rules[mandatory_rule]
    msg := sprintf("Service %s with %s destination missing mandatory rule %s", [input.name, destination, mandatory_rule])
}
