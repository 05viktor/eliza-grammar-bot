def is_comment(line):
    return line.startswith("#")


def is_empty_line(line):
    return line == ""


def string_without_comments(line):
    return line[:line.index("#")]


def normalize_lines(input_file):
    normalized_lines = []
    in_multiple_line_comment = False

    for raw_line in input_file.readlines():
        line = raw_line.strip()

        if is_comment(line) or is_empty_line(line):
            continue

        if "#" in line:
            line = string_without_comments(line).strip()
            if is_empty_line(line):
                continue

        if not in_multiple_line_comment and "/*" in line:
            in_multiple_line_comment = True
            comment_start_index = line.find("/*")

            if "*/" in line:
                last_comment_start_index = line.rfind("/*")
                last_comment_end_index = line.rfind("*/")

                if last_comment_start_index < last_comment_end_index:
                    in_multiple_line_comment = False
                    line = line[:comment_start_index] + line[last_comment_end_index + 2:]
                    line = line.strip()
            else:
                line = line[:comment_start_index].strip()

            if is_empty_line(line):
                continue

        elif in_multiple_line_comment:
            if "*/" in line:
                comment_end_index = line.rfind("*/")
                line = line[comment_end_index + 2:].strip()
                in_multiple_line_comment = False
                if is_empty_line(line):
                    continue
            else:
                continue

        normalized_lines.append(line)

    return normalized_lines


def parse_sections(input_file):
    sections = {}
    current_section = None

    for line in normalize_lines(input_file):
        if line.startswith("[") and line.endswith("]"):
            current_section = line[1:-1]
            if current_section not in sections:
                sections[current_section] = []
            continue

        if line == "End":
            current_section = None
            continue

        if current_section is None:
            continue

        sections[current_section].append(line)

    return sections
