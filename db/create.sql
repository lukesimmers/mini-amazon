CREATE TABLE Users (
    id INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    email VARCHAR UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    firstname VARCHAR(255) NOT NULL,
    lastname VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    balance DECIMAL DEFAULT 0,
    CHECK(balance >= 0)
);

CREATE TABLE Sellers (
    sid INTEGER NOT NULL PRIMARY KEY REFERENCES Users(id)
);

CREATE TABLE Category (
    name VARCHAR(255) NOT NULL PRIMARY KEY
);

-- For Products I changed Image constraints to allow Nulls.

CREATE TABLE Products (
    pid INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    seller_id INTEGER NOT NULL REFERENCES Sellers(sid),
    name VARCHAR(255) NOT NULL,
    description VARCHAR (1023) NOT NULL,
    category VARCHAR(255) NOT NULL REFERENCES Category(name),
    picture VARCHAR(255),
    price FLOAT NOT NULL,
    quantity_available INTEGER NOT NULL,
    CHECK(quantity_available >= 0)
);

CREATE TABLE OrderInformation (
    oid INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    uid INT NOT NULL REFERENCES Users(id),
    time_purchased timestamp without time zone NOT NULL DEFAULT (current_timestamp AT TIME ZONE 'UTC')
);

-- I would argue price_per_unit should be removed.

CREATE TABLE ItemsInOrder (
    oid INTEGER NOT NULL REFERENCES OrderInformation (oid),
    pid INT NOT NULL REFERENCES Products(pid),
    quantity INT NOT NULL, 
    price_per_unit FLOAT NOT NULL,
    fulfilled VARCHAR(32) NOT NULL,
    CHECK(fulfilled in ('Not Fulfilled', 'Fulfilled')),
    PRIMARY KEY(oid, pid)
);
    -- TRIGGER if quantity becomes NULL row is deleted

CREATE TABLE ProductReview (
    buyer_id INT REFERENCES Users(id),
    product_id INT REFERENCES Products(pid),
    rating INT NOT NULL,
    review VARCHAR(1023),
    CHECK(rating in (1,2,3,4,5)),
    PRIMARY KEY(buyer_id,product_id)
);

CREATE TABLE SellerReview (
    buyer_id INT REFERENCES Users(id),
    seller_id INT REFERENCES Sellers(sid),
    rating INT NOT NULL,
    review VARCHAR(1023),
    CHECK(rating in (1,2,3,4,5)),
    PRIMARY KEY(buyer_id, seller_id)
);

CREATE TABLE CARTS (
    uid INTEGER REFERENCES Users(id),
    pid INTEGER REFERENCES Products(pid),
    quantity INT NOT NULL, 
    price_when_placed FLOAT NOT NULL,
    CHECK(quantity > 0)
    -- Check if Carts(pid).price_when_placed = Products(pid).price when refrenced
    -- if not equal show a message and update uid, pid, quantity, price_when_placed not null
);

CREATE TABLE Messages (
    mid INT GENERATED BY DEFAULT AS IDENTITY PRIMARY KEY,
    sender_id INTEGER REFERENCES Users(id),
    recipient_id INTEGER REFERENCES Users(id),
    subject VARCHAR(255) NOT NULL,
    msg VARCHAR(1023) NOT NULL,
    msg_read VARCHAR(255) DEFAULT 'Unread',
    CHECK(msg_read in ('Unread', 'Read'))
);

-- Make check before insertion of reviews that user has purchase product/product from seller

-- Make check which prevents update of who a review is on.

-- Make check which prevents update of price per unit.


-- Added saved for later (same schema as )

-- Just to test out using views, product summary implementation will change later

CREATE VIEW ProductSummary(pid, name, description, category, price, review, rating, picture) AS
SELECT Products.pid, Products.name, Products.description, Products.category, Products.price, 
ProductReview.review,ProductReview.rating, Products.picture
FROM Products LEFT JOIN ProductReview ON Products.pid = ProductReview.product_id;

CREATE VIEW Purchases(id, uid, pid, time_purchased) AS
SELECT OrderInformation.oid, OrderInformation.uid, ItemsInOrder.pid, OrderInformation.time_purchased
FROM OrderInformation, ItemsInOrder
WHERE OrderInformation.oid = ItemsInOrder.oid;
