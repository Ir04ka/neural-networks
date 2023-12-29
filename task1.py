import logging
import argparse
import xml.etree.cElementTree as ET
from xml.dom import minidom


logger = logging.getLogger(__name__)


class InputException(Exception):
    """Exception raised for errors in the input file.

    Attributes:
        input_file -- input file's name
        line -- line that exception raised
    """

    def __init__(self, input_file, line):
        self.input_file = input_file
        self.line = line
        super().__init__()


class DataException(Exception):
    """Exception raised for logic errors .

    Attributes:
        input_file -- input file's name
        line -- line that exception raised
        message -- explanation of the error
    """

    def __init__(self, input_file, line, message):
        self.input_file = input_file
        self.line = line
        self.message = message
        super().__init__(message)


def validate_input_data(lines, input_file_name):
    for j in range(len(lines)):
        if '-' in lines[j]:
            raise InputException(input_file_name, j + 1)

        for e in lines[j]:
            if e.isalpha():
                raise InputException(input_file_name, j + 1)


    return True


def read_graph(input_file_name):

    with open(input_file_name, 'r') as input_graph:
        edges = {}

        lines = input_graph.read()
        lines = lines.replace(' ', '')
        lines = lines.split('\n')

        validate_input_data(lines, input_file_name)

        es = ''.join(lines)
        es = es.split('),(')
        max_vertex = max(int(es[0][1]), int(es[0][3]))

        for i in range(1, len(es)):
            max_vertex = max(max_vertex, int(es[i][0]), int(es[i][2]))

        in_number = [""] * max_vertex

        for i in range(len(es)):
            if i == 0:
                es[i] = es[i][1:]
            if i == len(es) - 1:
                if es[i][len(es[i]) - 1] == '\n':
                    es[i] = es[i][:len(es[i]) - 2]
                else:
                    es[i] = es[i][:-1]
            try:
                edge = eval(es[i])
                if len(edge) != 3:
                    edge = str(edge).replace(" ", '')
                    for j in range(len(lines)):
                        if edge in lines[j]:
                            raise InputException(input_file_name, j + 1)
            except SyntaxError:
                edge = str(edge).replace(" ", '')
                for j in range(len(lines)):
                    if edge in lines[j]:
                        raise InputException(input_file_name, j + 1)

            if edge[0] not in edges:
                edges[edge[0]] = []
            if edge[1] not in edges:
                edges[edge[1]] = []

            in_number[edge[1] - 1] = in_number[edge[1] - 1] + " " + str(edge[2])
            edges[edge[0]].append([edge[2], edge[1]])
    y = []

    for x in in_number:
        y.append(x.split(" "))
    for i in range(len(y)):
        num = []
        for j in range(1, len(y[i])):
            num.append(int(y[i][j]))
        num.sort()
        if len(num) == 1 and num[0] != 1:
            raise DataException(input_file_name, len(lines), 'Неправильная нумерация')
        for j in range(0, len(num) - 1):
            if num[j] == num[j + 1]:
                raise DataException(input_file_name, len(lines), 'Неправильная нумерация')
            if num[j + 1] - num[j] != 1:
                raise DataException(input_file_name, len(lines), 'Неправильная нумерация')
    return edges

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', required=True, help='Имя входного файла')
    parser.add_argument('-o', '--output', help='Имя выходного файла')
    parser.add_argument('--log-file', help='Имя файла с логом программы', dest='log_file')
    parser.add_argument('--log-level', help='Уровень логирования', dest='log_level', default='debug')

    args = parser.parse_args()

    numeric_level = getattr(logging, args.log_level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % args.log_level)

    logging.basicConfig(level=numeric_level, filename=args.log_file, encoding='utf-8')

    try:
        all_edges = read_graph(args.input)

        root = ET.Element("graph")

        for x in range(len(all_edges)):
            ET.SubElement(root, "vertex").text = 'v' + str(x + 1)
        for x in range(1, len(all_edges)):
            for z in range(len(all_edges[x])):
                arc = ET.SubElement(root, "arc")
                From = ET.SubElement(arc, 'from').text = 'v' + str(x)
                To = ET.SubElement(arc, 'to').text = 'v' + str(all_edges[x][z][1])
                Order = ET.SubElement(arc, 'order').text = str(all_edges[x][z][0])

        dom = minidom.parseString(ET.tostring(root))
        tree = dom.toprettyxml(indent='\t')

        if args.output is not None:
            with open(args.output, 'w') as file:
                file.write(tree)
        else:
            print(tree)
    except InputException as e:
        logging.fatal("Ошибка в данных входного файла %s в строке %s", e.input_file, e.line)
    except DataException as e:
        logging.fatal("Ошибка в логике данных входного файла %s в строке %s. Текст ошибки %s", e.input_file, e.line, e.message)
    except Exception as e:
        logging.fatal("Неизвестная ошибка")
        logging.exception(e)


if __name__ == '__main__':
    main()
