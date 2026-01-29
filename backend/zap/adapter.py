def zap_surface_to_endpoints(attack_surface, base_url):
    """
    Converts ZAP attack surface to a list of endpoint dictionaries with full URLs.
    """
    endpoints = []
    
    for item in attack_surface:
        # If we have the 'url' field (added in our fix), use it.
        # But we need to make sure it is absolute.
        # If it's relative, prepend base_url.
        
        raw_url = item.get("url", item.get("path", ""))
        
        if raw_url.startswith("http"):
            full_url = raw_url
        else:
            # Handle relative paths safely
            if not raw_url.startswith("/"):
                raw_url = "/" + raw_url
            full_url = base_url + raw_url
            
        endpoints.append({
            "url": full_url,
            "method": item.get("method", "GET"),
            "parameters": item.get("parameters", [])
        })
        
    return endpoints
