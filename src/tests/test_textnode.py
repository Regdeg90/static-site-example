import unittest
import pprint

from htmlnode import HTMLNode, LeafNode, ParentNode
from textnode import (
    TextNode,
    TextType,
    block_to_block_type,
    extract_markdown_images,
    extract_markdown_links,
    markdown_to_blocks,
    markdown_to_html_node,
    split_nodes_delimiter,
    split_nodes_image,
    split_nodes_link,
    text_node_to_html_node,
    text_to_textnodes,
)


class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a text node", TextType.BOLD)
        self.assertEqual(node, node2)

    def test_url(self):
        node = TextNode("This is a italic_node", TextType.ITALIC)
        self.assertEqual("TextNode(This is a italic_node, italic, None)", str(node))

    def test_not_eq(self):
        node = TextNode("This is a text node", TextType.BOLD)
        node2 = TextNode("This is a italic_node", TextType.ITALIC)
        self.assertNotEqual(node, node2)

    def test_textnode_to_htmlnode(self):
        self.assertEqual(
            "<i>This is a italic_node</i>",
            text_node_to_html_node(
                TextNode("This is a italic_node", TextType.ITALIC)
            ).to_html(),
        )


class TestHTMLNode(unittest.TestCase):
    def test_repr(self):
        node = HTMLNode("tag", "value", "children", "props")
        self.assertEqual("HTMLNode(tag, value, children, props)", str(node))

    def test_props_to_html(self):
        node = HTMLNode(props={"thing": "value", "thing2": "value2"})
        self.assertEqual('thing="value" thing2="value2"', node.props_to_html())


class TestLeafNode(unittest.TestCase):
    def test_val(self):
        node = LeafNode("p", "This is a paragraph of text.")
        self.assertEqual("<p>This is a paragraph of text.</p>", node.to_html())

    def test_props(self):
        node = LeafNode("a", "Click me!", {"href": "https://www.google.com"})
        self.assertEqual(
            '<a href="https://www.google.com">Click me!</a>', node.to_html()
        )


class TestParentNode(unittest.TestCase):
    def test_render(self):
        node = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
                LeafNode(None, "Normal text"),
                LeafNode("i", "italic text"),
                LeafNode(None, "Normal text"),
            ],
        )
        self.assertEqual(
            "<p><b>Bold text</b>Normal text<i>italic text</i>Normal text</p>",
            node.to_html(),
        )

    def test_multilevel(self):
        node1 = ParentNode(
            "p",
            [
                LeafNode("b", "Bold text"),
            ],
        )
        node2 = ParentNode("h1", [node1])
        self.assertEqual("<h1><p><b>Bold text</b></p></h1>", node2.to_html())


class TestSplitNodes(unittest.TestCase):
    def test_split(self):
        node = TextNode("This is text with a `code block` word", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "`", TextType.CODE)
        self.assertEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" word", TextType.TEXT),
            ],
            new_nodes,
        )

    def test_split_2(self):
        node = TextNode("This is text with a word that is *bold*", TextType.TEXT)
        new_nodes = split_nodes_delimiter([node], "*", TextType.BOLD)
        self.assertEqual(
            [
                TextNode("This is text with a word that is ", TextType.TEXT),
                TextNode("bold", TextType.BOLD),
            ],
            new_nodes,
        )


class TestExtractMethods(unittest.TestCase):
    def test_images(self):
        text = "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)"
        self.assertEqual(
            [
                ("rick roll", "https://i.imgur.com/aKaOqIh.gif"),
                ("obi wan", "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            extract_markdown_images(text),
        )

    def test_links(self):
        text = "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)"
        self.assertEqual(
            [
                ("to boot dev", "https://www.boot.dev"),
                ("to youtube", "https://www.youtube.com/@bootdotdev"),
            ],
            extract_markdown_links(text),
        )

    def test_split_links(self):
        node = TextNode(
            "This is text with a link [to boot dev](https://www.boot.dev) and [to youtube](https://www.youtube.com/@bootdotdev)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_link([node])
        self.assertEqual(
            [
                TextNode("This is text with a link ", TextType.TEXT),
                TextNode("to boot dev", TextType.LINK, "https://www.boot.dev"),
                TextNode(" and ", TextType.TEXT),
                TextNode(
                    "to youtube", TextType.LINK, "https://www.youtube.com/@bootdotdev"
                ),
            ],
            new_nodes,
        )

    def test_split_images(self):
        node = TextNode(
            "This is text with a ![rick roll](https://i.imgur.com/aKaOqIh.gif) and ![obi wan](https://i.imgur.com/fJRm4Vk.jpeg)",
            TextType.TEXT,
        )
        new_nodes = split_nodes_image([node])

        self.assertEqual(
            [
                TextNode("This is text with a ", TextType.TEXT),
                TextNode(
                    "rick roll", TextType.IMAGE, "https://i.imgur.com/aKaOqIh.gif"
                ),
                TextNode(" and ", TextType.TEXT),
                TextNode("obi wan", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            ],
            new_nodes,
        )

    def test_text_to_textnodes(self):
        text = "This is **text** with an *italic* word and a `code block` and an ![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)"
        self.assertEqual(
            [
                TextNode("This is ", TextType.TEXT),
                TextNode("text", TextType.BOLD),
                TextNode(" with an ", TextType.TEXT),
                TextNode("italic", TextType.ITALIC),
                TextNode(" word and a ", TextType.TEXT),
                TextNode("code block", TextType.CODE),
                TextNode(" and an ", TextType.TEXT),
                TextNode(
                    "obi wan image", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"
                ),
                TextNode(" and a ", TextType.TEXT),
                TextNode("link", TextType.LINK, "https://boot.dev"),
            ],
            text_to_textnodes(text),
        )
    
    def test_more_image_nodes(self):
        text = "![LOTR image artistmonkeys](/images/rivendell.png)"
        self.assertEqual([TextNode("LOTR image artistmonkeys", TextType.IMAGE, "/images/rivendell.png")], text_to_textnodes(text))
    
    def test_more_link_nodes(self):
        text = "[Back Home](/)"
        self.assertEqual([TextNode("Back Home", TextType.LINK, "/")], text_to_textnodes(text))
    
    def test_code(self):
        print(text_to_textnodes("An elaborate pantheon of deities (the `Valar` and `Maiar`)"))


class MarkdownMethods(unittest.TestCase):
    def test_markdown_to_blocks(self):
        markdown = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item"""
        self.assertEqual(
            [
                "# This is a heading",
                "This is a paragraph of text. It has some **bold** and *italic* words inside of it.",
                "* This is the first list item in a list block\n* This is a list item\n* This is another list item",
            ],
            markdown_to_blocks(markdown),
        )

    def test_block_to_block_type(self):
        markdown = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item

1. This
2. is
3. an
4. ordered
5. list"""
        self.assertEqual(
            ["heading", "paragraph", "unordered_list", "ordered_list"],
            [block_to_block_type(block) for block in markdown_to_blocks(markdown)],
        )

    def thingtest_markdown_to_html_node(self):
        markdown = """# This is a heading

This is a paragraph of text. It has some **bold** and *italic* words inside of it.

* This is the first list item in a list block
* This is a list item
* This is another list item

1. This
2. is
3. an
4. ordered
5. list"""
        self.maxDiff = None
        x = "HTMLNode(div, None, [HTMLNode(h1, None, [HTMLNode(None, This is a heading, None, None)], None), HTMLNode(p, None, [HTMLNode(None, This is a paragraph of text. It has some , None, None), HTMLNode(b, bold, None, None), HTMLNode(None,  and , None, None), HTMLNode(i, italic, None, None), HTMLNode(None,  words inside of it., None, None)], None), HTMLNode(ul, None, [HTMLNode(li, None, [HTMLNode(None,  This is the first list item in a list block, None, None)], None), HTMLNode(li, None, [HTMLNode(None,  This is a list item, None, None)], None), HTMLNode(li, None, [HTMLNode(None,  This is another list item, None, None)], None)], None), HTMLNode(ul, None, [HTMLNode(ol, None, [HTMLNode(None, This, None, None)], None), HTMLNode(ol, None, [HTMLNode(None, is, None, None)], None), HTMLNode(ol, None, [HTMLNode(None, an, None, None)], None), HTMLNode(ol, None, [HTMLNode(None, ordered, None, None)], None), HTMLNode(ol, None, [HTMLNode(None, list, None, None)], None)], None)], None)"
        self.assertEqual(x, str(markdown_to_html_node(markdown)))


if __name__ == "__main__":
    unittest.main()
