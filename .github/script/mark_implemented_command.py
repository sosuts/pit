import re


def update_readme(readme_path, implemented_commands):
    with open(
        readme_path,
    ) as f:
        lines = f.readlines()

    new_lines = []
    for line in lines:
        m = re.match(r"^(- \[.\]) (\w+)", line)
        if m:
            cmd = m.group(2)
            if cmd in implemented_commands:
                new_lines.append(f"- [x] {cmd}\n")
            else:
                new_lines.append(f"- [ ] {cmd}\n")
        else:
            new_lines.append(line)

    with open(readme_path, "w") as f:
        f.writelines(new_lines)


# pytestの出力からパスしたテスト関数名を抽出
implemented = set()
with open("pytest_result.log") as f:
    for line in f:
        # Pytestの結果から、test_xxx
        m = re.search(r"(test_([a-zA-Z0-9_]+)\.py\s([\.F]+))", line)
        if m:
            print(m.groups())
            implemented.add(m.group(2))

update_readme("README.md", implemented)
