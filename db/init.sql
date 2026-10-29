CREATE TABLE risks (
    id SERIAL PRIMARY KEY,
    asset TEXT NOT NULL,
    threat TEXT NOT NULL,
    likelihood INT NOT NULL,
    impact INT NOT NULL
);

INSERT INTO risks (asset, threat, likelihood, impact) VALUES
    ('Docker-образ', 'В образ попал секрет', 3, 5),
    ('Открытый порт', 'Сервис доступен шире, чем нужно', 2, 4),
    ('Учётная запись Hub', 'Слабый пароль на Docker Hub', 2, 5),
    ('База рисков', 'Нет резервной копии', 2, 4),
    ('Пайплайн GitLab', 'Токен Hub попал в лог CI', 2, 5);
