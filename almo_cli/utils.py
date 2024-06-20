def split_front_matter(md_content: str):
    """
    Splits the front matter from the markdown content.

    Args:
        md_content (str): The markdown content.

    Returns:
        Tuple[str, str]: The front matter and the markdown content.
    """

    # check content start with "---"
    if not md_content.startswith("---\n"):
        raise ValueError("Markdown content must start with '---'")

    parts = md_content.split("---", 2)

    front = parts[1].strip()
    content = parts[2].strip()

    return front, content
