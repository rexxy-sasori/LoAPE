Here's the revised implementation with user-configurable node preservation and updated documentation:

```markdown
# Kubernetes Node Scheduling Control Scripts

Scripts to manage pod scheduling by tainting/untainting nodes while keeping one node schedulable.

## 1. keep_one_node_schedulable.sh

**Purpose**: Taint all nodes with label `node_type=fusion` EXCEPT the specified node, preventing pod scheduling on tainted nodes.

### Features:
- Allows user to specify which node to keep untainted
- Configurable through command-line arguments
- Only affects nodes with label `node_type=fusion`
- Adds `worker=true:NoSchedule` taint to non-specified nodes
- Clear success/failure reporting

### Usage:
```bash
./keep_one_node_schedulable.sh [NODE_NAME_TO_KEEP]
```

### Parameters:
- `NODE_NAME_TO_KEEP` (required): Node to preserve from tainting

### Example:
```bash
chmod +x keep_one_node_schedulable.sh
./keep_one_node_schedulable.sh fusion-102

Expected output:
Preserving node: fusion-102
Adding NoSchedule taint to node: fusion-101
Successfully tainted node: fusion-101
```

## 2. untaint_all_nodes.sh

**Purpose**: Remove all `worker=true:NoSchedule` taints from ALL nodes

### Features:
- Removes taints from all nodes regardless of labels
- Full cleanup of specified taint
- Clear operation feedback

### Usage:
```bash
chmod +x untaint_all_nodes.sh
./untaint_all_nodes.sh
```

## Prerequisites

1. `kubectl` configured with cluster access
2. Bash environment
3. Kubernetes nodes with proper labels
