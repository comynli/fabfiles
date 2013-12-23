#!/bin/bash
echo "{{name}}"
[[ -d /tmp ]] && echo "tmp"
echo "{{age|default(18)}}"
whoami