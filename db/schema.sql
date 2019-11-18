CREATE TABLE news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_date INTEGER NOT NULL,
    modified_date INTEGER NOT NULL,
    title TEXT,
    content TEXT
);
CREATE TABLE comment
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    created_date INTEGER NOT NULL,
    modified_date INTEGER NOT NULL,
    news_id INTEGER NOT NULL,
    content TEXT,
    CONSTRAINT comment_news_id_fk FOREIGN KEY (news_id) REFERENCES news (id) ON DELETE CASCADE
);