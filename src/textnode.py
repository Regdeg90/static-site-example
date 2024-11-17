from enum import Enum

from htmlnode import HTMLNode, LeafNode, ParentNode
import re


class TextType(Enum):
    TEXT = "text"
    BOLD = "bold"
    ITALIC = "italic"
    CODE = "code"
    LINK = "link"
    IMAGE = "image"


class TextNode:
    def __init__(self, text, text_type, url=None):
        self.text = text
        self.text_type = text_type
        self.url = url

    def __eq__(self, text_node):
        if not isinstance(text_node, TextNode):
            return False
        return all(
            [
                text_node.text == self.text,
                text_node.text_type == self.text_type,
                text_node.url == self.url,
            ]
        )

    def __repr__(self):
        return f"TextNode({self.text}, {self.text_type.value}, {self.url})"


def text_node_to_html_node(text_node):
    tpe = text_node.text_type
    if tpe == TextType.TEXT:
        return LeafNode(None, text_node.text)
    if tpe == TextType.BOLD:
        return LeafNode("b", text_node.text)
    if tpe == TextType.ITALIC:
        return LeafNode("i", text_node.text)
    if tpe == TextType.CODE:
        return LeafNode("code", text_node.text)
    if tpe == TextType.LINK:
        return LeafNode("a", text_node.text, props={"href": text_node.url})
    if tpe == TextType.IMAGE:
        return LeafNode("img", "", props={"src": text_node.url, "alt": text_node.text})
    raise Exception("Unsupported node type")


def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []
    for node in old_nodes:
        if not node.text and not node.url:
            continue
        if node.text_type != TextType.TEXT or delimiter not in node.text:
            new_nodes.append(node)
        else:
            split = node.text.split(delimiter)
            new_nodes.extend(
                [TextNode(split[0], TextType.TEXT), TextNode(split[1], text_type)]
            )
            new_nodes.extend(
                split_nodes_delimiter(
                    [TextNode("".join(split[2:]), TextType.TEXT)], delimiter, text_type
                )
            )

    return new_nodes


def extract_markdown_images(text):
    matches = re.findall(r"\s!\[.*?\]\(.*?\)", text)
    ret = []

    for m in matches:
        x = m.split("](")
        ret.append((x[0][3:], x[1][:-1]))
    return ret


def extract_markdown_links(text):
    matches = re.findall(r"\s\[.*?\]\(.*?\)", text)
    ret = []

    for m in matches:
        x = m.split("](")
        ret.append((x[0][2:], x[1][:-1]))
    return ret


def split_nodes_image(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        matches = re.findall(r"\s!\[.*?\]\(.*?\)", node.text)
        text = node.text
        for m in matches:
            if not text:
                break
            left_text, text = text.split(m, maxsplit=1)
            x = m.split("](")
            new_nodes.extend(
                [
                    TextNode(left_text + " ", TextType.TEXT),
                    TextNode(x[0][3:], TextType.IMAGE, url=x[1][:-1]),
                ]
            )
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes


def split_nodes_link(old_nodes):
    new_nodes = []

    for node in old_nodes:
        if node.text_type != TextType.TEXT:
            new_nodes.append(node)
            continue
        matches = re.findall(r"\s\[.*?\]\(.*?\)", node.text)
        text = node.text
        for m in matches:
            if not text:
                break
            left_text, text = text.split(m, maxsplit=1)
            x = m.split("](")
            new_nodes.extend(
                [
                    TextNode(left_text + " ", TextType.TEXT),
                    TextNode(x[0][2:], TextType.LINK, url=x[1][:-1]),
                ]
            )
        if text:
            new_nodes.append(TextNode(text, TextType.TEXT))

    return new_nodes


def text_to_textnodes(text):
    nodes = [TextNode(text=text, text_type=TextType.TEXT)]
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "*", TextType.ITALIC)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    return nodes


def markdown_to_blocks(markdown):
    ret = []
    for line in markdown.split("\n\n"):
        if line == "":
            continue
        line = line.strip()
        ret.append(line)
    return ret


def block_to_block_type(markdown):
    if not markdown:
        return "paragraph"

    l = len(markdown)

    if re.findall(r"^[#+]{1,6}", markdown):
        return "heading"
    if l > 5 and markdown[:2] == "```" and markdown[:2] == markdown[-2:]:
        return "code"
    if all([x[0] == ">" for x in markdown.split("\n")]):
        return "quote"
    if all([x[0] in "*-" for x in markdown.split("\n")]):
        return "unordered_list"
    is_para = False
    for i, x in enumerate(markdown.split("\n")):
        if len(x) < 3:
            is_para = True
            break
        if x[:3] == f"{i+1}. ":
            continue
        is_para = True
        break
    return "paragraph" if is_para else "ordered_list"


def markdown_to_html_node(markdown):
    children = []
    for block in markdown_to_blocks(markdown):
        tpe = block_to_block_type(block)
        if tpe == "paragraph":
            children.append(
                ParentNode(
                    tag="p",
                    children=[
                        text_node_to_html_node(node)
                        for node in text_to_textnodes(block)
                    ],
                )
            )
        elif tpe == "heading":
            cnt = 0
            for x in block:
                if x != "#":
                    break
                cnt += 1
            block = block[cnt:]
            children.append(
                ParentNode(
                    tag=f"h{cnt}",
                    children=[
                        text_node_to_html_node(node)
                        for node in text_to_textnodes(block[cnt:])
                    ],
                )
            )
        elif tpe == "code":
            b = block.rstrip("```").lstrip("```")
            children.append(
                ParentNode(
                    tag="pre",
                    children=[
                        ParentNode(
                            tag="code",
                            children=[
                                text_node_to_html_node(node)
                                for node in text_to_textnodes(b)
                            ],
                        )
                    ],
                )
            )
        elif tpe == "unordered_list":
            sub_children = []
            for l in block.split("\n"):
                sub_children.append(
                    ParentNode(
                        tag="li",
                        children=[
                            text_node_to_html_node(node)
                            for node in text_to_textnodes(l[1:])
                        ],
                    )
                )
            children.append(ParentNode(tag="ul", children=sub_children))
        elif tpe == "ordered_list":
            sub_children = []
            for l in block.split("\n"):
                _, x = l.split(" ", maxsplit=1)
                sub_children.append(
                    ParentNode(
                        tag="ol",
                        children=[
                            text_node_to_html_node(node)
                            for node in text_to_textnodes(x)
                        ],
                    )
                )
            children.append(ParentNode(tag="ul", children=sub_children))
        elif tpe == "quote":
            sub_children = []
            for l in block.split("\n"):
                sub_children.extend(
                    [text_node_to_html_node(node) for node in text_to_textnodes(l[1:])]
                )
            children.append(
                ParentNode(
                    tag="blockquote",
                    children=sub_children,
                )
            )

    return HTMLNode(tag="div", children=children)
