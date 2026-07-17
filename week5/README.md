# Week5

Task 2:
```sql
CREATE DATABASE website;

CREATE TABLE member (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    follower_count INT UNSIGNED NOT NULL DEFAULT 0,
    time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id)
);
```
<img width="1200" height="799" alt="image" src="https://github.com/user-attachments/assets/6b8afa67-b7db-4052-a6ce-78e9f77772eb" />


Task 3:
```sql
INSERT INTO member (name, email, password) VALUES ('test', 'test@test.com', 'test');
INSERT INTO member (name, email, password, follower_count) VALUES ('Jordan', 'jordanfisher@test.com', 'j0000', '384');
INSERT INTO member (name, email, password, follower_count) VALUES
('Talia', 'taliaryder@test.com', 't0000', '40');
INSERT INTO member (name, email, password, follower_count) VALUES
('Sam', 'samclaflin@test.com', 's0000', '389');
INSERT INTO member (name, email, password, follower_count) VALUES
('Lily', 'lilycollins@test.com', 'l0000', '2848');

SELECT * FROM member;
SELECT * FROM member ORDER BY time DESC;
SELECT * FROM member ORDER BY time DESC LIMIT 1, 3;
SELECT * FROM member WHERE email = 'test@test.com';
SELECT * FROM member WHERE name LIKE '%es%';
SELECT * FROM member WHERE email = 'test@test.com' AND password = 'test';
UPDATE member SET name = 'test2' WHERE email = 'test@test.com';
```
<img width="1684" height="541" alt="image" src="https://github.com/user-attachments/assets/d462eb82-923a-40d7-b742-74e15e28326f" />
<img width="1150" height="704" alt="image" src="https://github.com/user-attachments/assets/46596e9d-cdc4-4d5e-865f-79db6e9e0901" />
<img width="1386" height="784" alt="image" src="https://github.com/user-attachments/assets/0f209ecf-e822-4511-8c77-42f57974473f" />
<img width="1198" height="457" alt="image" src="https://github.com/user-attachments/assets/80c43570-a306-43bc-a71c-028b96ae983f" />


Task 4:
```sql
SELECT COUNT(*) FROM member;
SELECT SUM(follower_count) FROM member;
SELECT AVG(follower_count) FROM member;

SELECT AVG(top_two.follower_count) 
FROM (
    SELECT follower_count FROM member ORDER BY follower_count DESC LIMIT 2
) AS top_two;
```
<img width="904" height="729" alt="image" src="https://github.com/user-attachments/assets/1c430cf7-ea76-4b54-9d0f-6ad90a66e03f" />
<img width="1042" height="418" alt="image" src="https://github.com/user-attachments/assets/b63a1feb-070b-4d3b-88cf-6b6f1ba128bd" />


Task 5:
```sql
CREATE TABLE message (
    id INT UNSIGNED NOT NULL AUTO_INCREMENT,
    member_id INT UNSIGNED NOT NULL,
    content TEXT NOT NULL,
    like_count INT UNSIGNED NOT NULL DEFAULT 0,
    time DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    FOREIGN KEY (member_id) REFERENCES member(id)
);

SELECT message.id, member.name, message.content, message.like_count, message.time FROM message
JOIN member ON message.member_id = member.id;

SELECT message.id, member.name, member.email, message.content, message.like_count, message.time FROM message
JOIN member ON message.member_id = member.id
WHERE member.email = 'test@test.com';

SELECT AVG(message.like_count) 
FROM message
JOIN member ON message.member_id = member.id
WHERE member.email = 'test@test.com';

SELECT member.email, AVG(message.like_count)
FROM message
JOIN member ON message.member_id = member.id
GROUP BY member.email;
```
<img width="1015" height="646" alt="image" src="https://github.com/user-attachments/assets/c8e43050-efd1-4e7e-a4a5-7ef3a0e62520" />
<img width="1379" height="694" alt="image" src="https://github.com/user-attachments/assets/6f24665f-20e3-4680-869f-5b84f5fc8518" />
<img width="714" height="640" alt="image" src="https://github.com/user-attachments/assets/d889b861-298c-48f2-a018-86a1099e124d" />
