CREATE TABLE user (
  user_id int(16) NOT NULL AUTO_INCREMENT,
  username varchar(32) NOT NULL,
  password varchar(32) NOT NULL,
  email varchar(64) NOT NULL,
  first_name varchar(32),
  last_name varchar(32),
  PRIMARY KEY (user_id),
  UNIQUE KEY (username)
) AUTO_INCREMENT=1;

CREATE TABLE task_list (
  task_list_id int(16) NOT NULL AUTO_INCREMENT,
  name varchar(32) NOT NULL,
  PRIMARY KEY (task_list_id)
) AUTO_INCREMENT=1;

CREATE TABLE parent (
  parent_id int(16) NOT NULL AUTO_INCREMENT,
  user_id int(16) NOT NULL,
  task_list_id int(16) NOT NULL,
  PRIMARY KEY (parent_id),
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (task_list_id) REFERENCES task_list(task_list_id)
) AUTO_INCREMENT=1;
