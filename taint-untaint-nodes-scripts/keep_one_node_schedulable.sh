#!/bin/bash

SAVE_NODE="fusion-101"

# Get all node names from the Kubernetes cluster
nodes=$(kubectl get nodes -l node_type=fusion --no-headers -o custom-columns=":metadata.name")

# Loop through the node names
for node in $nodes; do
  # Skip the node named 'fusion-101'
  if [[ $node == $SAVE_NODE ]]; then
    echo "Skipping node: $node"
    continue
  fi
  
  # Check if the node name contains 'intel'
  if [[ $node != $SAVE_NODE ]]; then
    echo "Adding NoSchedule taint to node: $node"
    
    # Add NoSchedule taint to the node
    kubectl taint nodes $node worker=true:NoSchedule
    
    # Check if taint was successfully applied
    if [[ $? -eq 0 ]]; then
      echo "Successfully tainted node: $node"
    else
      echo "Failed to taint node: $node"
    fi
  fi
done

