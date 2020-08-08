from pathlib import Path
import spacy
import redis


nlp = spacy.load("en_core_web_sm")
redis_client = redis.Redis(host="172.20.0.2", port=6379)


def get_filters():
    return (
        lambda token: token.is_stop,
        lambda token: token.is_space,
        lambda token: token.is_punct,
    )


def parse_text(data):
    parsed_text = nlp(data)
    words = []
    filters = get_filters()
    for word in parsed_text:
        if not any((filter_(word) for filter_ in filters)):
            words.append(word.lemma_.lower())
    return words


def index_words(index_name, file_id, data, words):
    redis_client.hset(f"__{index_name}", file_id, data)
    for word in words:
        key = f"{index_name}::{file_id}"
        redis_client.hincrby(word, key, 1)


def search(index_name, words):
    docs = []
    for word in words:
        docs_ = redis_client.hgetall(word)
        for doc_, count_ in docs_.items():
            doc_ = doc_.decode()
            count = int(count_.decode())
            index_name_, file_id = doc_.split('::')
            print(file_id)
            if index_name_ == index_name:
                docs.append(redis_client.hget(f"__{index_name}", file_id).decode())
    return docs                   


def index_file(index_name, file_, index=False):
    with open(file_, "r") as f:
        data = f.read()
    file_id = Path(file_).stem
    words = parse_text(data)
    if index:
        index_words(index_name, file_id, data, words)
    else:
        print(file_id)
        print(",".join(words))
