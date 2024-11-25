use drugdatabase;
CREATE TABLE customer (
 uid varchar(20) NOT NULL,
 pass varchar(20) DEFAULT NULL,
 fname varchar(15) DEFAULT NULL,
 lname varchar(15) DEFAULT NULL,
 email varchar(30) DEFAULT NULL,
 address varchar(128) DEFAULT NULL,
 phno bigint DEFAULT NULL,
 PRIMARY KEY (uid)
);
CREATE TABLE product (
 pid varchar(15) NOT NULL,
 pname varchar(20) DEFAULT NULL,
 manufacturer varchar(20) DEFAULT NULL,
 mfg date DEFAULT NULL,
 exp date DEFAULT NULL,
 price int DEFAULT NULL,
 PRIMARY KEY (pid),
 UNIQUE KEY pname (pname)
);
CREATE TABLE inventory (
 pid varchar(15) NOT NULL,
 pname varchar(20) DEFAULT NULL,
 quantity int unsigned DEFAULT NULL,
 sid varchar(15) NOT NULL,
 PRIMARY KEY (pid,sid),
 CONSTRAINT fk01 FOREIGN KEY (pid) REFERENCES product (pid) ON DELETE CASCADE,
 CONSTRAINT fk02 FOREIGN KEY (pname) REFERENCES product (pname) ON DELETE
CASCADE,
 CONSTRAINT fk03 FOREIGN KEY (sid) REFERENCES seller (sid) ON DELETE CASCADE
);
CREATE TABLE orders (
oid int NOT NULL AUTO_INCREMENT,
pid varchar(15) DEFAULT NULL,
sid varchar(15) DEFAULT NULL,
uid varchar(15) DEFAULT NULL,
orderdatetime datetime DEFAULT NULL,
quantity int unsigned DEFAULT NULL,
price int unsigned DEFAULT NULL,
PRIMARY KEY (oid),
CONSTRAINT fk04 FOREIGN KEY (pid) REFERENCES product (pid) ON DELETE CASCADE,
CONSTRAINT fk05 FOREIGN KEY (sid) REFERENCES seller (sid) ON DELETE CASCADE,
CONSTRAINT fk06 FOREIGN KEY (uid) REFERENCES customer (uid) ON DELETE CASCADE
);
CREATE TABLE low_stock_report (
 report_id INT NOT NULL AUTO_INCREMENT,
 pid VARCHAR(15) NOT NULL,
 pname VARCHAR(20) DEFAULT NULL,
 sid VARCHAR(15) NOT NULL,
 quantity INT UNSIGNED DEFAULT NULL,
 report_datetime DATETIME DEFAULT NULL,
 PRIMARY KEY (report_id),
 CONSTRAINT fk07 FOREIGN KEY (pid) REFERENCES product (pid) ON DELETE CASCADE,
 CONSTRAINT fk08 FOREIGN KEY (sid) REFERENCES seller (sid) ON DELETE CASCADE
);
CREATE TABLE price_history (
 history_id INT NOT NULL AUTO_INCREMENT,
 pid VARCHAR(15) NOT NULL,
 old_price INT NOT NULL,
 new_price INT NOT NULL,
 change_date DATETIME DEFAULT NOW(),
 PRIMARY KEY (history_id),
 FOREIGN KEY (pid) REFERENCES product(pid) ON DELETE CASCADE
);
delimiter //
CREATE TRIGGER updatetime BEFORE INSERT ON orders FOR EACH ROW
BEGIN
 SET NEW.orderdatetime = NOW();
END//
delimiter ;
DELIMITER //
CREATE TRIGGER inventorytrigger AFTER INSERT ON orders
FOR EACH ROW
begin
DECLARE qnty int;
DECLARE productid varchar(20);
SELECT pid INTO productid
FROM orders
ORDER BY oid DESC
LIMIT 1;
SELECT quantity INTO qnty
FROM orders
ORDER BY oid DESC
LIMIT 1;
UPDATE inventory
SET quantity=quantity-qnty
WHERE pid=productid;
END//
DELIMITER ;
delimiter //
CREATE TRIGGER log_price_change BEFORE UPDATE ON product
FOR EACH ROW
BEGIN
 IF OLD.price != NEW.price THEN
 INSERT INTO price_history (pid, old_price, new_price, change_date)
 VALUES (OLD.pid, OLD.price, NEW.price, NOW());
 END IF;
END //
delimiter ;
delimiter //
CREATE PROCEDURE getorders
(IN param1 VARCHAR(20))
BEGIN
 SELECT * FROM orders WHERE uid=param1;
END //
delimiter ;
delimiter //
CREATE PROCEDURE check_low_stock(IN updated_pid VARCHAR(15), IN
updated_quantity INT UNSIGNED)
BEGIN
 DECLARE pname VARCHAR(20);
 DECLARE sid VARCHAR(15);

 -- Get product name and seller ID based on the updated PID
 SELECT pname, sid INTO pname, sid FROM product WHERE pid = updated_pid;

 -- Check if quantity is less than 5
 IF updated_quantity < 5 THEN
 INSERT INTO low_stock_report (pid, pname, sid, quantity, report_datetime)
 VALUES (updated_pid, pname, sid, updated_quantity, NOW());
 END IF;
END //
delimiter ;


