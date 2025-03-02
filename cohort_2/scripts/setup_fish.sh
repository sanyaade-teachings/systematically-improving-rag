#!/usr/bin/env fish

# Get the directory where the script is located
set script_dir (dirname (status -f))
set env_path "$script_dir/../.env"

# Check for .env
if not test -f $env_path
  echo "No .env file found at $env_path"
  exit 1
end

# Read each non-comment line from .env.
# Fish doesn't allow "export VAR=val" in one step; we use `set -x`.
for line in (cat $env_path | grep -v '^#' | grep .)
    set key (echo $line | cut -d '=' -f1)
    set value (echo $line | cut -d '=' -f2-)
    # -x exports the variable to the environment
    set -x $key $value
end

echo "Environment variables from $env_path have been set"
