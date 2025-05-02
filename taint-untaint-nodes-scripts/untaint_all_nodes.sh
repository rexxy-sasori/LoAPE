#!/bin/bash

# Get all node names from the Kubernetes cluster
nodes=$(kubectl get nodes --no-headers -o custom-columns=":metadata.name")

# Loop through the node names
for node in $nodes; do
  # Check if the node name contains 'intel'
  #if [[ $node == *"fusion"* ]]; then
    echo "Removing NoSchedule taint from node: $node"
    
    # Remove NoSchedule taint from the node
    kubectl taint nodes $node worker=true:NoSchedule-
    
    # Check if taint was successfully removed
    if [[ $? -eq 0 ]]; then
      echo "Successfully untainted node: $node"
    else
      echo "Failed to untaint node: $node"
    fi
  #fi
done

