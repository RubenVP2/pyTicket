-- Delete table if exists
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS ticket;

-- table for users
CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL,
  isAdmin BIT NOT NULL
);

-- table for ticket
CREATE TABLE ticket (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  client_id INTEGER NOT NULL,
  date_ticket TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  sujet_ticket TEXT NOT NULL,
  description_ticket TEXT NOT NULL,
  etat_ticket TEXT NOT NULL DEFAULT 'non résolu',
  FOREIGN KEY (client_id) REFERENCES user (id)
);

-- insert values to user

INSERT INTO user (username, password, isAdmin )
VALUES
  ('antoine', 'antoine01', true),
  ('maxence', 'maxence69', true),
  ('ruben', 'ruben99', true),
  ('client1', 'client1', false),
  ('client2', 'client2', false);

-- insert values to ticket
  INSERT INTO ticket (client_id, date_ticket, sujet_ticket, description_ticket, etat_ticket)
  VALUES
    (4, 1604488312, 'Imprimante non fonctionnelle', "Depuis que mon collègue a renversé son café sur l'imprimante elle imprime en noir et blanc uniquement", false),
    (4, 1591269112, "Ordinateur n'a plus de réseau", "L'ordinateur du stagiaire ne peut pas se connecter au réseau interne", true),
    (5, 1604315512, 'Serveur indisponible', "Serveur indisponible depuis coupure de courant, le site web est indisponible", false),
    (5, 1549278712, "Fibre non performante", "L'ordinateur du stagiaire ne peut pas se connecter au réseau interne", true);
