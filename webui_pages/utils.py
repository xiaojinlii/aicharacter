

def format_character_name(cid: int, name: str):
    formatted_id = str(cid).zfill(5)
    return f"{formatted_id} - {name}"
