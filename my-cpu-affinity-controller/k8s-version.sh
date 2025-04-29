#!/bin/bash
set -euo pipefail

# Print the version being processed
VERSION=${1#"v"}
if [ -z "$VERSION" ]; then
    echo "Must specify version!"
    exit 1
fi
echo "Processing Kubernetes version: ${VERSION}"

# Fetch the list of modules to replace
echo "Fetching module replacements from Kubernetes go.mod..."
MODS=($(
    curl -sS https://raw.githubusercontent.com/kubernetes/kubernetes/v${VERSION}/go.mod |
    sed -n 's|.*k8s.io/\(.*\) => ./staging/src/k8s.io/.*|k8s.io/\1|p'
))
echo "Found ${#MODS[@]} modules to replace:"
printf '%s\n' "${MODS[@]}"

# Replace each module in the local go.mod file
for MOD in "${MODS[@]}"; do
    echo "Processing module: ${MOD}"
    V=$(
        go mod download -json "${MOD}@kubernetes-${VERSION}" |
        sed -n 's|.*"Version": "\(.*\)".*|\1|p'
    )
    echo "Resolved version for ${MOD}: ${V}"
    echo "Adding replace directive for ${MOD} => ${MOD}@${V}"
    go mod edit "-replace=${MOD}=${MOD}@${V}"
done

# Add the Kubernetes dependency
echo "Adding Kubernetes dependency: k8s.io/kubernetes@v${VERSION}"
go get "k8s.io/kubernetes@v${VERSION}"

echo "Done!"