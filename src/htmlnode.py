class HTMLNode:
    def __init__(self, tag=None, value=None, children=None, props=None):
        self.tag = tag
        self.value = value
        self.children = children
        self.props = props

    def __repr__(self):
        return f"HTMLNode({self.tag}, {self.value}, {self.children}, {self.props})"

    def to_html(self):
        raise NotImplementedError()

    def props_to_html(self):
        return (
            " ".join(f'{key}="{val}"' for key, val in self.props.items())
            if self.props
            else ""
        )


class LeafNode(HTMLNode):
    def __init__(self, tag=None, value=None, props=None):
        super().__init__(tag=tag, value=value, children=None, props=props)

    def to_html(self):
        if not self.value:
            raise Exception("must have a value")
        if not self.tag:
            return str(self.value)
        props_render = f" {self.props_to_html()}" if self.props else ""
        return f"<{self.tag}{props_render}>{self.value}</{self.tag}>"


class ParentNode(HTMLNode):
    def __init__(self, tag, children, props=None):
        super().__init__(tag=tag, value=None, children=children, props=props)

    def to_html(self):
        if not self.tag:
            raise ValueError("must have a tag")
        if not self.children:
            raise ValueError("must have children")

        return f"<{self.tag}>{''.join(x.to_html() for x in self.children)}</{self.tag}>"
