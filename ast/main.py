import ast
with open("sample.py", "r", encoding="utf-8") as f:
    code = f.read()
    tree = ast.parse(code)
    for node in ast.walk(tree):
        print(node)
        print(node.__dict__)
        print("children: " + str([x for x in ast.iter_child_nodes(node)]) + "\\n")