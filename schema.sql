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
  date_ticket TIMESTAMP DEFAULT CURRENT_TIMESTAMP NOT NULL,
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
  ('lola', 'porcora', false),
  ('luffy', 'elastik', false),
  ('fabrice', 'cerqueira', false),
  ('olivier', 'oudin', false),
  ('price','jhon',false);


-- insert values to ticket
INSERT INTO ticket (client_id, date_ticket, sujet_ticket, description_ticket, etat_ticket)
 VALUES
   (4, '2020-11-15 14:59:07', 'Imprimante non fonctionnelle', "Depuis que mon collègue a renversé son café sur l'imprimante elle imprime en noir et blanc uniquement", 'résolu'),
   (4, '2018-08-08 14:59:07', "Ordinateur n'a plus de réseau", "L'ordinateur du stagiaire ne peut pas se connecter au réseau interne", 'non résolu'),
   (7, '2012-09-23 14:16:07', 'Serveur indisponible', "Serveur indisponible depuis coupure de courant, le site web est indisponible", 'en cours de résolution'),
   (6, '2020-11-12 11:14:07', "Fibre non performante", "L'ordinateur du stagiaire ne peut pas se connecter au réseau interne", 'résolu'),
   (5, '2020-11-01 12:12:07', "Problème licence Microsoft", "ma licence Microsoft est terminée", 'en cours de résolution'),
   (6, '2020-11-10 14:50:07', "Fibre non performante", "L'ordinateur du stagiaire ne peut pas se connecter au réseau interne", 'non résolu'),
   (7, '2020-10-10 11:53:07', "Pc portable qui ne fonctionne pas", "mon Pc portable ne s'allume plus ...", 'résolu'),
   (7, '2020-11-10 14:59:07', "mot de passe oublié", "j'ai oublié mon mot de passe pour me connecter au site de l'entreprise!", 'non résolu'),
   (5, '2020-11-10 14:59:07', "Perdu mon telephone", "J'ai oublié mon telephone dans le vogue merry serait-il possible dans avoir un nouveau?", 'non résolu'),
   (8, '2020-03-10 14:59:07', "virus sur l'ordinateur", "je vais avoir besoin d'une INTERVENTION car j'ai pris un virus en utilisant RUST", 'non résolu'),
   (8, '2020-03-10 14:59:07', "virus sur l'ordinateur", "je vais avoir besoin d'une INTERVENTION car j'ai pris un virus en utilisant RUST", 'non résolu');
