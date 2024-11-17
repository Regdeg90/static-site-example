import os
import shutil
from textnode import TextNode, extract_header, markdown_to_html_node, text_node_to_html_node


def  generate_page(from_path, template_path, dest_path):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")
    from_file = ""
    with open(from_path) as f:
        from_file = f.read()
    template_file = ""
    with open(template_path) as f:
        template_file = f.read()

    
    # print(markdown_to_html_node(from_file))
    # print("above is markdown --------------")
    template_file = template_file.replace("{{ Content }}", markdown_to_html_node(from_file).to_html())
    template_file = template_file.replace("{{ Title }}", extract_header(from_file))
    with open(dest_path, "w") as f:
        f.write(template_file)


def generate_page_recur(dir_path_content, template_path, dest_dir_path):
    if not os.path.exists(dir_path_content):
        return
    for file in os.listdir(dir_path_content):
        source_file = os.path.join(dir_path_content, file)
        dest_file = os.path.join(dest_dir_path, file)
        if os.path.isdir(source_file):
            os.mkdir(dest_file)
            generate_page_recur(source_file, template_path, dest_file)
        else:
            if ".md" in file:
                dest_file = dest_file.replace(".md", ".html")
                generate_page(source_file, template_path, dest_file)


def recur_copy(source, destination):
    if not os.path.exists(source):
        return
    for file in os.listdir(source):
        source_file = os.path.join(source, file)
        dest_file = os.path.join(destination, file)
        if os.path.isdir(source_file):
            os.mkdir(dest_file)
            recur_copy(source_file, dest_file)
        else:
            shutil.copy(source_file, dest_file)


def main():
    shutil.rmtree("public", ignore_errors=True)
    os.mkdir("public")
    recur_copy("static", "public")
    # generate_page("content/index.md", "template.html", "public/index.html")
    # print(os.path.abspath("template.html"))
    generate_page_recur("content", os.path.abspath("template.html"), "public")
    # print(os.path.abspath("template.html"))

if __name__ == "__main__":
    main()
