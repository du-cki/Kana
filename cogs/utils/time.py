def sing(amount : int, unit : str, breif : bool) -> str:
    """singularizer(?) - returns a string containing the amount 
    and type of something. The type/unit of item will be pluralized
    if the amount is greater than one."""
    if breif:   return f"{amount}{amount == 1 and f'{unit}' or f'{unit}'}"
    return f"{amount} {amount == 1 and f'{unit}' or f'{unit}s'}"

def deltaconv(seconds : int, breif : bool) -> str:
    """Converts a timedelta's total_seconds() to a humanized string."""
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    dys, hrs = divmod(hrs, 24)
    
    timedict = {'day': dys, 'hour': hrs, 'minute': mins, 'second': secs}
    if breif:   timedict = {'d': dys, 'h': hrs, 'm': mins, 's': secs}

    cleaned = {k:v for k,v in timedict.items() if v != 0}
    return " ".join(sing(v, k, breif) for k,v in cleaned.items())