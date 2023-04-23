from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy.orm import relationship
from sqlalchemy_serializer import SerializerMixin
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

app = Flask(__name__)
app.secret_key = 'sda'
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todoapp.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
Bootstrap(app)
db = SQLAlchemy(app)


class Board(db.Model, SerializerMixin):
    __tablename__ = "boards"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))

    todo_tasks = relationship("TodoTask", back_populates="board")
    doing_tasks = relationship("DoingTask", back_populates="board")
    done_tasks = relationship("DoneTask", back_populates="board")


class TodoTask(db.Model, SerializerMixin):
    __tablename__ = "todo_tasks"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"))
    board = relationship("Board", back_populates="todo_tasks")
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)


class DoingTask(db.Model, SerializerMixin):
    __tablename__ = "doing_tasks"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"))
    board = relationship("Board", back_populates="doing_tasks")
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)


class DoneTask(db.Model, SerializerMixin):
    __tablename__ = "done_tasks"
    id = db.Column(db.Integer, primary_key=True)
    board_id = db.Column(db.Integer, db.ForeignKey("boards.id"))
    board = relationship("Board", back_populates="done_tasks")
    title = db.Column(db.String(250), nullable=False)
    description = db.Column(db.Text, nullable=False)


db.create_all()


@app.route('/',  methods=["GET", "POST"])
def home():
    id = request.args.get("id")
    all_boards = db.session.query(Board).all()
    boards = [board_obj for board_obj in all_boards]
    if id:
        board = db.session.query(Board).get(id)
        if request.method == "POST":
            tag = request.form.get('tag')
            task_id = request.form.get('task_id')
            edit_mode = request.form.get('edit_mode')

            title = request.form.get('task-title', type=str)
            description = request.form.get('task-description')
            if tag == '0':
                if edit_mode == 'true':
                    task = TodoTask.query.get(task_id)
                    task.title = title
                    task.description = description
                else:
                    new_task = TodoTask(
                        board_id=id,
                        title=title,
                        description=description
                        )
                    db.session.add(new_task)
            elif tag == '1':
                if edit_mode == 'true':
                    task = DoingTask.query.get(task_id)
                    task.title = title
                    task.description = description
                else:
                    new_task = DoingTask(
                        board_id=id,
                        title=title,
                        description=description
                        )
                    db.session.add(new_task)
            elif tag == '2':
                if edit_mode == 'true':
                    task = DoneTask.query.get(task_id)
                    task.title = title
                    task.description = description
                else:
                    new_task = DoneTask(
                        board_id=id,
                        title=title,
                        description=description
                        )
                    db.session.add(new_task)
            db.session.commit()
        return render_template('index.html', boards=boards, board=board, has_goto=True, id_to_add=id)
    return render_template("index.html", boards=boards, has_goto=False)


@app.route('/delete')
def delete():
    id = request.args.get("id")
    board_to_delete = Board.query.get(id)
    if board_to_delete != None:
        for task in board_to_delete.todo_tasks:
            db.session.delete(task)
        for task in board_to_delete.doing_tasks:
            db.session.delete(task)
        for task in board_to_delete.done_tasks:
            db.session.delete(task)
        db.session.delete(board_to_delete)
        db.session.commit()
    return redirect(url_for('home'))

@app.route('/delete_task')
def delete_task():
    id = request.args.get("id")
    tag = request.args.get("tag")
    if tag == '0':
        task_to_delete = TodoTask.query.get(id)
    elif tag == '1':
        task_to_delete = DoingTask.query.get(id)
    elif tag == '2':
        task_to_delete = DoneTask.query.get(id)
    db.session.delete(task_to_delete)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/add", methods=["POST"])
def add():
    new_board = Board(
        name=request.form.get('name', type=str),
    )
    db.session.add(new_board)
    db.session.commit()
    return redirect(url_for('home'))

@app.route("/contact", methods=['POST'])
def contact():
    if request.method == "POST":
        message = Mail(
            from_email='tairko2007@gmail.com',
            to_emails='tairko2007@gmail.com',
            subject='New Message',
            html_content=f'Name: { request.form.get("name") } | Email: {request.form.get("email") } | Phone: {request.form.get("phone_number") } | Message: «{request.form.get("message")}»'
        )
        try:
            sg = SendGridAPIClient('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')
            response = sg.send(message)
            print(response.status_code)
            print(response.body)
            print(response.headers)
        except Exception as e:
            print(e.message)
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
