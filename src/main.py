from textnode import NodeType, TextNode


def main():
    node = TextNode("testing", NodeType.LEAF, "a_url")

    print(node)


if __name__ == "__main__":
    main()
