def sing(amount: int, unit: str, brief: bool) -> str:
    """
    singularizer(?) - returns a string containing the amount 
    and type of something. The type/unit of item will be pluralized
    if the amount is greater than one.
    
    :param amount: The time.
    :type amount: int
    :param unit: The unit of time.
    :type unit: str
    :param brief: Whether to use the brief format or not.
    :type brief: bool
    """
    if brief:
        return f"{amount}{amount == 1 and f'{unit}' or f'{unit}'}"
    return f"{amount} {amount == 1 and f'{unit}' or f'{unit}s'}"

def deltaconv(seconds: int, brief: bool = False) -> str:
    """
    Converts a timedelta's total_seconds() to a humanized string.
    
    :param seconds: The amount of seconds to convert.
    :type seconds: int
    :param brief: Whether to use the brief format or not.
    :type brief: bool
    """
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    dys, hrs = divmod(hrs, 24)
    
    timedict = {'day': dys, 'hour': hrs, 'minute': mins, 'second': secs}
    if brief:   timedict = {'d': dys, 'h': hrs, 'm': mins, 's': secs}

    cleaned = {k:v for k,v in timedict.items() if v != 0}
    return " ".join(sing(v, k, brief) for k,v in cleaned.items())
