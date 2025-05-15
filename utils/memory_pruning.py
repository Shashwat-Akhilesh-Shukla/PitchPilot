from typing import Dict, List, Any

def prune_memory(memory_items: List[Dict[str, Any]], threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Prune memory items based on relevance.
    
    Args:
        memory_items: List of memory items to prune
        threshold: Relevance threshold for pruning
        
    Returns:
        Pruned list of memory items
    """
    # This is a simplified implementation
    # In a real system, this would use sophisticated relevance scoring
    
    # Keep items with relevance score above threshold
    pruned_items = []
    for item in memory_items:
        relevance = item.get("relevance", 0.0)
        if relevance >= threshold:
            pruned_items.append(item)
    
    return pruned_items
