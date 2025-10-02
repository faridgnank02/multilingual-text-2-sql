-- Base de données d'exemple : Librairie
-- Tables : Auteurs, Livres, Emprunts, Utilisateurs

CREATE TABLE Auteurs (
    AuteurID INTEGER PRIMARY KEY,
    Nom TEXT NOT NULL,
    Prenom TEXT NOT NULL,
    DateNaissance DATE,
    Nationalite TEXT
);

CREATE TABLE Livres (
    LivreID INTEGER PRIMARY KEY,
    Titre TEXT NOT NULL,
    AuteurID INTEGER,
    Genre TEXT,
    DatePublication DATE,
    NombrePages INTEGER,
    ISBN TEXT UNIQUE,
    FOREIGN KEY (AuteurID) REFERENCES Auteurs (AuteurID)
);

CREATE TABLE Utilisateurs (
    UtilisateurID INTEGER PRIMARY KEY,
    Nom TEXT NOT NULL,
    Prenom TEXT NOT NULL,
    Email TEXT UNIQUE,
    DateInscription DATE,
    Telephone TEXT
);

CREATE TABLE Emprunts (
    EmpruntID INTEGER PRIMARY KEY,
    LivreID INTEGER,
    UtilisateurID INTEGER,
    DateEmprunt DATE,
    DateRetourPrevue DATE,
    DateRetourEffective DATE,
    FOREIGN KEY (LivreID) REFERENCES Livres (LivreID),
    FOREIGN KEY (UtilisateurID) REFERENCES Utilisateurs (UtilisateurID)
);

-- Insertion des données d'exemple

-- Auteurs
INSERT INTO Auteurs (Nom, Prenom, DateNaissance, Nationalite) VALUES
('Camus', 'Albert', '1913-11-07', 'Française'),
('Rowling', 'J.K.', '1965-07-31', 'Britannique'),
('Garcia Marquez', 'Gabriel', '1927-03-06', 'Colombienne'),
('Orwell', 'George', '1903-06-25', 'Britannique'),
('Proust', 'Marcel', '1871-07-10', 'Française'),
('Tolkien', 'J.R.R.', '1892-01-03', 'Britannique'),
('Hugo', 'Victor', '1802-02-26', 'Française'),
('Hemingway', 'Ernest', '1899-07-21', 'Américaine');

-- Livres
INSERT INTO Livres (Titre, AuteurID, Genre, DatePublication, NombrePages, ISBN) VALUES
('L''Étranger', 1, 'Philosophique', '1942-01-01', 123, '978-2070360024'),
('Harry Potter à l''école des sorciers', 2, 'Fantasy', '1997-06-26', 309, '978-2070541270'),
('Cent ans de solitude', 3, 'Réalisme magique', '1967-05-30', 417, '978-2070360697'),
('1984', 4, 'Dystopie', '1949-06-08', 328, '978-2070368228'),
('Du côté de chez Swann', 5, 'Littéraire', '1913-11-14', 531, '978-2070360031'),
('Le Seigneur des anneaux', 6, 'Fantasy', '1954-07-29', 1216, '978-2070612888'),
('Les Misérables', 7, 'Historique', '1862-03-30', 1488, '978-2070360253'),
('Le Vieil Homme et la Mer', 8, 'Littéraire', '1952-09-01', 127, '978-2070360116'),
('La Chute', 1, 'Philosophique', '1956-05-16', 176, '978-2070360048'),
('Harry Potter et la Chambre des secrets', 2, 'Fantasy', '1998-07-02', 364, '978-2070541287');

-- Utilisateurs
INSERT INTO Utilisateurs (Nom, Prenom, Email, DateInscription, Telephone) VALUES
('Martin', 'Jean', 'jean.martin@email.com', '2023-01-15', '0123456789'),
('Dubois', 'Marie', 'marie.dubois@email.com', '2023-02-20', '0123456790'),
('Petit', 'Pierre', 'pierre.petit@email.com', '2023-03-10', '0123456791'),
('Bernard', 'Sophie', 'sophie.bernard@email.com', '2023-04-05', '0123456792'),
('Rousseau', 'Paul', 'paul.rousseau@email.com', '2023-05-12', '0123456793'),
('Lefebvre', 'Anne', 'anne.lefebvre@email.com', '2023-06-18', '0123456794'),
('Moreau', 'Michel', 'michel.moreau@email.com', '2023-07-22', '0123456795'),
('Simon', 'Julie', 'julie.simon@email.com', '2023-08-30', '0123456796');

-- Emprunts
INSERT INTO Emprunts (LivreID, UtilisateurID, DateEmprunt, DateRetourPrevue, DateRetourEffective) VALUES
(1, 1, '2024-01-10', '2024-01-24', '2024-01-22'),
(2, 2, '2024-01-15', '2024-01-29', NULL),
(3, 3, '2024-01-20', '2024-02-03', '2024-02-01'),
(4, 1, '2024-02-05', '2024-02-19', NULL),
(5, 4, '2024-02-10', '2024-02-24', '2024-02-23'),
(6, 5, '2024-02-15', '2024-03-01', NULL),
(7, 2, '2024-02-20', '2024-03-06', NULL),
(8, 6, '2024-02-25', '2024-03-11', '2024-03-09'),
(9, 7, '2024-03-01', '2024-03-15', NULL),
(10, 8, '2024-03-05', '2024-03-19', NULL);