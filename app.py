
from flask import Flask, request, render_template
import sqlite3

app = Flask(__name__)


def open_db():
    conn = sqlite3.connect('db_author.db')
    return conn


def close_db(conn):
    conn.close()


@app.route('/')
def lists():
    root_author = list_of_root_author()
    coauthor = list_of_coauthor()
    return render_template('main.html', root_author=root_author, coauthor=coauthor)


def list_of_root_author():
    root_author = []
    conn = open_db()
    cursor = conn.execute('SELECT RealName FROM AUTHOR')
    for row in cursor:
        root_author.append(row[0])
    root_author.sort()
    close_db(conn)
    return root_author


def list_of_coauthor():
    coauthor = []
    conn = open_db()
    cursor = conn.execute('SELECT Coauthor FROM AUTHOR')
    for row in cursor:
        coat = row[0].split(', ')
        for i in range(len(coat)):
            coat[i] = coat[i].replace("'", '')
            if coat[i][0] is '"':
                coat[i] = coat[i][1:-1]
            if coat[i].title() not in coauthor:
                coauthor.append(coat[i].title())
    coauthor.sort()
    close_db(conn)
    return coauthor


def find_name(name, conn):
    cursor = conn.execute('SELECT Author FROM AUTHOR WHERE RealName = "' + name + '"')
    for row in cursor:
        return row[0]


@app.route('/result')
def start():
    root_author = list_of_root_author()
    coauthor = list_of_coauthor()
    conn = open_db()
    gr = []
    level = {}
    tops = {}
    top = []
    for_tops = 1

    real = request.args.get('author', '')

    if real is '':
        error = 'Seems empty <Root Author>'
        return render_template('main.html', error=error, root_author=root_author, coauthor=coauthor)
    find = request.args.get('coauthor', '').lower()

    if find is '':
        error = 'Seems empty <Co-Author>'
        return render_template('main.html', error=error, root_author=root_author, coauthor=coauthor)

    name = find_name(real, conn)

    if name == find:
        error = 'Seems you choose the same person'
        return render_template('main.html', error=error, root_author=root_author, coauthor=coauthor)

    level[name] = -1
    tops[name] = 0
    top.append(name)

    def add(name, for_tops):
        flag = 0
        cursor = conn.execute('SELECT Coauthor FROM AUTHOR WHERE Author = "' + name + '"')
        for row in cursor:
            flag = 1
            coaut = row[0].split(', ')
            for i in range(len(coaut)):
                coaut[i] = coaut[i].replace("'", '')
            gr.append(coaut)
            for i in coaut:
                if i not in level.keys():
                    level[i] = -1
                    tops[i] = for_tops
                    top.append(i)
                    for_tops += 1
        if flag is 0:
            gr.append([])
        return for_tops

    while top:
        j = top.pop(0)
        if j is None:
            error = "Seems like a typo. Try again, select from the list"
            return render_template('main.html', error=error, root_author=root_author, coauthor=coauthor)
        if j[0] is '"':
            j = j[1:-1]
        for_tops = add(j, for_tops)

    close_db(conn)

    def find_path(s):
        level[s] = 0
        queue = [s]
        short_path = [[s]]
        while queue:
            v = queue.pop(0)
            way = short_path.pop(0)
            for w in gr[tops[v]]:
                if level.get(w) == -1:
                    queue.append(w)
                    level[w] = level[v] + 1
                    short_path.append(way + [w])
                if w == find:
                    return level[w], short_path[-1]

    if level.get(name) == -1:
        result = find_path(name)
        if result is None:
            error = "Seems like " + name.title() + " and " + find.title() + " have nothing in common." \
                                                                            " Try again, select from the list"
            return render_template('main.html', error=error, root_author=root_author, coauthor=coauthor)
        result_number, result_path = result
        text = "This means that " + find.title() + " related to " + name.title() + " via " + str(
            result_number - 1) + " person"
        return render_template('main.html', result_number=result_number, text=text, result_path=result_path[:-1],
                               name=name.title(), find=find.title(), root_author=root_author, coauthor=coauthor)


if __name__ == '__main__':
    app.run()
