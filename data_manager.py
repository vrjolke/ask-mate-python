import bcrypt
from connection import connection_handler
from datetime import datetime


def hash_password(plain_text_password):
    # By using bcrypt, the salt is saved into the hash itself
    hashed_bytes = bcrypt.hashpw(plain_text_password.encode('utf-8'), bcrypt.gensalt())
    return hashed_bytes.decode('utf-8')


@connection_handler
def register_new_user(cursor, new_user):
    pw_to_hash = new_user['password']
    hashed_pw = hash_password(pw_to_hash)
    new_user['hashed_pw'] = hashed_pw

    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_user['reg_date'] = str(dt)

    cursor.execute("""
        INSERT INTO registered_users (username, hashed_pw, reg_date)
        VALUES (%(username)s, %(hashed_pw)s, %(reg_date)s);
        """, new_user)


@connection_handler
def check_username_in_database(cursor, new_user):
    cursor.execute("""
        SELECT * FROM registered_users
        WHERE username=%(username)s;
        """, new_user)
    username = cursor.fetchall()

    if len(username) == 0:
        return False
    else:
        return True


def verify_password(plain_text_password, hashed_password):
    this_was_hashed = plain_text_password
    hashed_bytes_password = hashed_password.encode('utf-8')
    return bcrypt.checkpw(this_was_hashed.encode('utf-8'), hashed_bytes_password)


@connection_handler
def verify_user(cursor, login_data):
    cursor.execute("""
        SELECT * FROM registered_users
        WHERE username=%(username)s;
        """, login_data)

    stored_hash_password = cursor.fetchall()

    if len(stored_hash_password) == 0:
        return False
    else:
        password = login_data['password']
        stored_hash_password_from_db = stored_hash_password[0]['hashed_pw']
        pw_check = verify_password(password, stored_hash_password_from_db)
        return pw_check


@connection_handler
def update_view_counter(cursor, question_id, increment):
    current_question = get_record_by_id("question", question_id)[0]

    current_question['view_number'] += increment
    new_view_number = current_question['view_number']

    cursor.execute(f"""
        UPDATE question
        SET view_number = {new_view_number}
        WHERE id = {question_id};
        """)


def get_back_image_name(new_image_name):
    new_image_name = new_image_name.split()
    new_image_name = new_image_name[1].replace("'", '')
    return new_image_name


@connection_handler
def get_database(cursor, which_database):
    cursor.execute(f"""
        SELECT * FROM {which_database}
        ORDER BY submission_time DESC;
        """)
    database = cursor.fetchall()
    return database


@connection_handler
def get_limited_database(cursor, which_database, limit):
    cursor.execute(f"""
        SELECT * FROM {which_database}
        ORDER BY submission_time DESC
        LIMIT {limit};
        """)
    database = cursor.fetchall()
    return database


@connection_handler
def insert_new_question_to_database(cursor, new_data):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_data['submission_time'] = str(dt)

    cursor.execute("""
        INSERT INTO question
        (submission_time, view_number, vote_number, title, message, image, user_id)
        VALUES (%(submission_time)s, %(view_number)s, %(vote_number)s, %(title)s, %(message)s, %(image)s, %(user_id)s);
        """, new_data)


@connection_handler
def insert_new_answer_to_database(cursor, new_data):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_data['submission_time'] = str(dt)

    cursor.execute("""
        INSERT INTO answer
        (submission_time, vote_number, question_id, message, image, user_id)
        VALUES (%(submission_time)s, %(vote_number)s, %(question_id)s, %(message)s, %(image)s, %(user_id)s);
        """, new_data)


@connection_handler
def get_record_by_id(cursor, which_database, id):
    cursor.execute(f"""
        SELECT q.*, r.username
        FROM {which_database} q
        LEFT JOIN registered_users r ON q.user_id = r.id
        WHERE q.id = {id};
        """)
    record = cursor.fetchall()
    return record


@connection_handler
def update_question(cursor, updated_data, question_id):
    new_data = list(updated_data.values())
    cursor.execute(f"""
        UPDATE question
        SET title = %s,
            message = %s,
            image = %s
        WHERE id = {question_id};
        """, new_data)


@connection_handler
def update_answer(cursor, updated_data, answer_id):
    new_data = list(updated_data.values())
    cursor.execute(f"""
        UPDATE answer
        SET message = %s,
            image = %s
        WHERE id = {answer_id};
        """, new_data)


@connection_handler
def get_answers_by_question_id(cursor, question_id):
    cursor.execute(f"""
        SELECT answer.*, r.username FROM answer
        LEFT JOIN registered_users r ON answer.user_id = r.id
        WHERE question_id = {question_id}
        ORDER BY submission_time;
        """)
    current_answers = cursor.fetchall()
    return current_answers


@connection_handler
def delete_every_answer_by_question_id(cursor, question_id):
    current_answers = get_answers_by_question_id(question_id)
    list_of_answer_ids = []
    for answer in current_answers:
        list_of_answer_ids.append(int(answer['id']))

    for answer_id in list_of_answer_ids:
        cursor.execute(f"""
            DELETE FROM answer
            WHERE id = {answer_id};
            """)


@connection_handler
def delete_question_and_answers(cursor, question_id):
    cursor.execute(f"""
        DELETE FROM comment
        WHERE question_id = {question_id};
    """)

    delete_every_answer_by_question_id(question_id)

    cursor.execute(f"""
        DELETE FROM question
        WHERE id = {question_id};
        """)


@connection_handler
def delete_single_answer_by_id(cursor, answer_id):
    cursor.execute(f"""
        DELETE FROM comment
        WHERE answer_id = {answer_id};
        """)

    cursor.execute(f"""
        DELETE FROM answer
        WHERE id = {answer_id};
        """)


@connection_handler
def delete_single_comment_by_id(cursor, comment_id):
    cursor.execute(f"""
        DELETE FROM comment
        WHERE id = {comment_id};
        """)


@connection_handler
def sort_data(cursor, key, table, order):
    cursor.execute(f"""
        SELECT * FROM {table}
        ORDER BY {key} {order}
        """)
    result = cursor.fetchall()
    return result


@connection_handler
def vote_counter(cursor, table, id, up_or_down):
    if up_or_down == "up":
        vote_change = 1
    else:
        vote_change = -1

    cursor.execute(f"""
        UPDATE {table}
        SET vote_number = vote_number + {vote_change}
        WHERE id = {id}
        """)


@connection_handler
def get_question_id_by_answer_id(cursor, answer_id, table='answer'):
    cursor.execute(f"""
        SELECT question_id from {table}
        WHERE id = {answer_id}
        """)
    question_id = cursor.fetchall()
    return question_id[0]['question_id']


@connection_handler
def get_question_id_by_comment_id(cursor, comment_id):
    cursor.execute(f"""
        SELECT question_id from comment
        WHERE id = {comment_id}
        """)
    question_id = cursor.fetchall()
    return question_id[0]['question_id']


@connection_handler
def get_search_results_from_database(cursor, which_database, id, column, search_data):
    cursor.execute(f"""
        SELECT {id} from {which_database}
        WHERE {column} ILIKE '%{search_data}%'
        """)
    ids = cursor.fetchall()

    list_of_ids = []
    if which_database == "question":
        for element in ids:
            list_of_ids.append(element['id'])
    else:
        for element in ids:
            list_of_ids.append(element['question_id'])
    return list_of_ids


@connection_handler
def get_search_results(cursor, search_data, key):
    question_ids_from_title = get_search_results_from_database("question", 'id', 'title', search_data)
    question_ids_from_message = get_search_results_from_database("question", 'id', 'message', search_data)
    answer_ids_from_message = get_search_results_from_database("answer", 'question_id', 'message', search_data)

    question_ids_for_search = question_ids_from_title + question_ids_from_message + answer_ids_from_message
    unique_question_ids = tuple(set(question_ids_for_search))

    if len(unique_question_ids) == 1:
        unique_question_id = list(unique_question_ids)[0]
        cursor.execute(f"""
            SELECT * from question
            WHERE id = {unique_question_id}
            ORDER BY {key} DESC;
            """)
    elif len(unique_question_ids) == 0:
        cursor.execute(f"""
            SELECT * from question
            WHERE id = -1
            ORDER BY {key} DESC;
            """)
    else:
        cursor.execute(f"""
            SELECT * from question
            WHERE id IN {unique_question_ids}
            ORDER BY {key} DESC;
            """)

    search_results = cursor.fetchall()
    number_of_results = len(search_results)
    return search_results, number_of_results


@connection_handler
def insert_new_question_comment_to_database(cursor, new_comment_data):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_comment_data['submission_time'] = str(dt)

    cursor.execute("""
        INSERT INTO comment
        (question_id, message, submission_time, edited_count, user_id)
        VALUES (%(question_id)s, %(message)s, %(submission_time)s, %(edited_count)s, %(user_id)s)
        """, new_comment_data)


@connection_handler
def insert_new_answer_comment_to_database(cursor, new_comment_data):
    dt = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    new_comment_data['submission_time'] = str(dt)

    cursor.execute("""
        INSERT INTO comment
        (question_id, answer_id, message, submission_time, edited_count, user_id)
        VALUES (%(question_id)s, %(answer_id)s, %(message)s, %(submission_time)s, %(edited_count)s, %(user_id)s)
        """, new_comment_data)


@connection_handler
def get_comments_by_question_id(cursor, question_id):
    cursor.execute(f"""
        SELECT comment.*, r,username FROM comment
        LEFT JOIN registered_users r on comment.user_id = r.id
        WHERE question_id = {question_id} AND answer_id IS NULL
        ORDER BY submission_time;
        """)
    comments = cursor.fetchall()
    return comments


@connection_handler
def get_answer_comments(cursor):
    cursor.execute(f"""
        SELECT comment.*, r.username FROM comment
        LEFT JOIN registered_users r on comment.user_id = r.id
        ORDER BY submission_time;
        """)
    comments = cursor.fetchall()
    return comments


@connection_handler
def get_comment_by_comment_id(cursor, which_database, comment_id):
    cursor.execute(f"""
        SELECT * FROM {which_database}
        WHERE id = {comment_id};
        """)
    comment = cursor.fetchall()
    return comment[0]


@connection_handler
def update_data_by_id(cursor, which_database, new_data, id):
    comment = get_comment_by_comment_id('comment', id)
    comment['edited_count'] += 1
    new_edited_count = comment['edited_count']

    data_to_update = list(new_data.values())
    cursor.execute(f"""
                    UPDATE {which_database}
                    SET message = %s , edited_count = {new_edited_count}
                    WHERE id = {id}
                    """, data_to_update)


@connection_handler
def get_user_id_by_username(cursor, username):
    user = dict()
    user['username'] = username
    cursor.execute("""
        SELECT id FROM registered_users
        WHERE username = %(username)s;
        """, user)
    user_id = cursor.fetchall()
    return user_id[0]['id']


@connection_handler
def get_all_user_data(cursor):
    cursor.execute("""
            SELECT id, username, reg_date FROM registered_users;
            """)
    user_table = cursor.fetchall()
    return user_table

