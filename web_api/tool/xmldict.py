"""
    xmldict
    ~~~~~~~~~~~~~~~~~~~~~~~~~
    Modified from https://github.com/thoughtnirvana/xmldict

    Convert xml to python dictionaries.
"""
import datetime


def xml_to_dict(root_or_str, strict=True):
    """
    Converts `root_or_str` which can be parsed xml or a xml string to dict.

    """
    root = root_or_str
    if isinstance(root, str):
        import xml.etree.cElementTree as ElementTree

        root = ElementTree.XML(root_or_str)
    return {root.tag: _from_xml(root, strict)}


def dict_to_xml(dict_xml):
    """
    Converts `dict_xml` which is a python dict to corresponding xml.
    """
    return _to_xml(dict_xml)


# Functions below this line are implementation details.
# Unless you are changing code, don't bother reading.
# The functions above constitute the user interface.


def _to_xml(el):
    """
    Converts `el` to its xml representation.
    """
    val = None
    if isinstance(el, dict):
        val = _dict_to_xml(el)
    elif isinstance(el, bool):
        val = str(el).lower()
    else:
        val = el
    if val is None:
        val = "null"
    return val


def _extract_attrs(els):
    """
    Extracts attributes from dictionary `els`. Attributes are keys which start
    with '@'
    """
    if not isinstance(els, dict):
        return ""
    return "".join(
        ' %s="%s"' % (key[1:], value)
        for key, value in els.items()
        if key.startswith("@")
    )


def _dict_to_xml(els):
    """
    Converts `els` which is a python dict to corresponding xml.
    """

    def process_content(tag, content):
        attrs = _extract_attrs(content)
        text = isinstance(content, dict) and content.get("#text", "") or ""
        return "<%s%s>%s%s</%s>" % (tag, attrs, _to_xml(content), text, tag)

    tags = []
    for tag, content in els.items():
        # Text and attributes
        if tag.startswith("@") or tag == "#text":
            continue
        elif isinstance(content, list):
            for el in content:
                tags.append(process_content(tag, el))
        elif isinstance(content, dict):
            tags.append(process_content(tag, content))
        else:
            tags.append("<%s>%s</%s>" % (tag, _to_xml(content), tag))
    return "".join(tags)


def _str_to_datetime(date_str):
    try:
        val = datetime.datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        val = date_str
    return val


def _str_to_boolean(bool_str):
    if bool_str.lower() != "false" and bool(bool_str):
        return True
    return False


def _from_xml(el, strict):
    """
    Extracts value of xml element element `el`.
    """
    val = None
    # Parent node.
    val = {}
    if len(el):
        for e in el:
            tag = e.tag
            v = _from_xml(e, strict)
            if tag in val:
                # Multiple elements share this tag, make them a list
                if not isinstance(val[tag], list):
                    val[tag] = [val[tag]]
                val[tag].append(v)
            else:
                # First element with this tag
                val[tag] = v

    attribs = el.items()
    # An element with attributes.
    if attribs and strict:
        val.update(dict(("@%s" % k, v) for k, v in dict(attribs).items()))
        if el.text:
            converted = _val_and_maybe_convert(el)
            val["#text"] = el.text
            if converted != el.text:
                val["#value"] = converted
    #    elif el.text:
    #        # An element with no subelements but text.
    #        val.update(_val_and_maybe_convert(el))
    elif attribs:
        val.update(dict(attribs))
    return val


def _val_and_maybe_convert(el):
    """
    Converts `el.text` if `el` has attribute `type` with valid value.
    """
    text = el.text.strip()
    data_type = el.get("type")
    convertor = _val_and_maybe_convert.convertors.get(data_type)
    if convertor:
        return convertor(text)
    else:
        return text


_val_and_maybe_convert.convertors = {  # type: ignore
    "boolean": _str_to_boolean,
    "datetime": _str_to_datetime,
    "integer": int,
}
