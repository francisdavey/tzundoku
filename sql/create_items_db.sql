CREATE TABLE items (
item_id INT(6) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
doku_id INT(6) NOT NULL,
title VARCHAR(30) NOT NULL,
year VARCHAR(50),
director VARCHAR(30),
image VARCHAR(200),
description VARCHAR(200),
created_by_ID INT(6) UNSIGNED DEFAULT 2,
created_date TIMESTAMP
)
