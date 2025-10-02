-- Base de données d'exemple : École
-- Tables : Étudiants, Cours, Professeurs, Inscriptions, Notes

CREATE TABLE Professeurs (
    ProfesseurID INTEGER PRIMARY KEY,
    Nom TEXT NOT NULL,
    Prenom TEXT NOT NULL,
    Email TEXT UNIQUE,
    Departement TEXT,
    DateEmbauche DATE
);

CREATE TABLE Cours (
    CoursID INTEGER PRIMARY KEY,
    NomCours TEXT NOT NULL,
    CodeCours TEXT UNIQUE,
    Credits INTEGER,
    ProfesseurID INTEGER,
    Semestre TEXT,
    FOREIGN KEY (ProfesseurID) REFERENCES Professeurs (ProfesseurID)
);

CREATE TABLE Etudiants (
    EtudiantID INTEGER PRIMARY KEY,
    Nom TEXT NOT NULL,
    Prenom TEXT NOT NULL,
    Email TEXT UNIQUE,
    DateNaissance DATE,
    Promotion INTEGER,
    Specialite TEXT
);

CREATE TABLE Inscriptions (
    InscriptionID INTEGER PRIMARY KEY,
    EtudiantID INTEGER,
    CoursID INTEGER,
    DateInscription DATE,
    Statut TEXT DEFAULT 'Actif',
    FOREIGN KEY (EtudiantID) REFERENCES Etudiants (EtudiantID),
    FOREIGN KEY (CoursID) REFERENCES Cours (CoursID)
);

CREATE TABLE Notes (
    NoteID INTEGER PRIMARY KEY,
    InscriptionID INTEGER,
    TypeEvaluation TEXT,
    Note REAL,
    DateEvaluation DATE,
    Coefficient REAL DEFAULT 1.0,
    FOREIGN KEY (InscriptionID) REFERENCES Inscriptions (InscriptionID)
);

-- Insertion des données d'exemple

-- Professeurs
INSERT INTO Professeurs (Nom, Prenom, Email, Departement, DateEmbauche) VALUES
('Dupont', 'Jean', 'jean.dupont@ecole.fr', 'Informatique', '2015-09-01'),
('Lefranc', 'Marie', 'marie.lefranc@ecole.fr', 'Mathématiques', '2018-02-15'),
('Girard', 'Paul', 'paul.girard@ecole.fr', 'Physique', '2016-09-01'),
('Rousseau', 'Sophie', 'sophie.rousseau@ecole.fr', 'Informatique', '2019-09-01'),
('Blanchard', 'Michel', 'michel.blanchard@ecole.fr', 'Mathématiques', '2017-02-01'),
('Lemoine', 'Julie', 'julie.lemoine@ecole.fr', 'Chimie', '2020-09-01');

-- Cours
INSERT INTO Cours (NomCours, CodeCours, Credits, ProfesseurID, Semestre) VALUES
('Programmation Python', 'INFO101', 6, 1, 'S1'),
('Structures de données', 'INFO201', 6, 4, 'S2'),
('Base de données', 'INFO301', 4, 1, 'S3'),
('Analyse mathématique', 'MATH101', 8, 2, 'S1'),
('Algèbre linéaire', 'MATH201', 6, 5, 'S2'),
('Physique générale', 'PHYS101', 6, 3, 'S1'),
('Statistiques', 'MATH301', 4, 2, 'S3'),
('Chimie organique', 'CHIM201', 6, 6, 'S2');

-- Étudiants
INSERT INTO Etudiants (Nom, Prenom, Email, DateNaissance, Promotion, Specialite) VALUES
('Martin', 'Alice', 'alice.martin@student.fr', '2003-05-15', 2024, 'Informatique'),
('Durand', 'Bob', 'bob.durand@student.fr', '2003-08-22', 2024, 'Informatique'),
('Petit', 'Claire', 'claire.petit@student.fr', '2003-03-10', 2024, 'Mathématiques'),
('Bernard', 'David', 'david.bernard@student.fr', '2002-12-05', 2023, 'Physique'),
('Thomas', 'Emma', 'emma.thomas@student.fr', '2003-07-18', 2024, 'Informatique'),
('Robert', 'François', 'francois.robert@student.fr', '2002-11-30', 2023, 'Mathématiques'),
('Richard', 'Gabrielle', 'gabrielle.richard@student.fr', '2003-04-25', 2024, 'Chimie'),
('Dubois', 'Hugo', 'hugo.dubois@student.fr', '2002-09-12', 2023, 'Informatique');

-- Inscriptions
INSERT INTO Inscriptions (EtudiantID, CoursID, DateInscription, Statut) VALUES
(1, 1, '2023-09-01', 'Actif'),
(1, 4, '2023-09-01', 'Actif'),
(1, 6, '2023-09-01', 'Actif'),
(2, 1, '2023-09-01', 'Actif'),
(2, 4, '2023-09-01', 'Actif'),
(3, 4, '2023-09-01', 'Actif'),
(3, 5, '2024-02-01', 'Actif'),
(4, 6, '2022-09-01', 'Terminé'),
(4, 4, '2022-09-01', 'Terminé'),
(5, 1, '2023-09-01', 'Actif'),
(5, 2, '2024-02-01', 'Actif'),
(6, 4, '2022-09-01', 'Terminé'),
(6, 5, '2023-02-01', 'Terminé'),
(7, 8, '2024-02-01', 'Actif'),
(8, 1, '2022-09-01', 'Terminé'),
(8, 2, '2023-02-01', 'Terminé'),
(8, 3, '2023-09-01', 'Actif');

-- Notes
INSERT INTO Notes (InscriptionID, TypeEvaluation, Note, DateEvaluation, Coefficient) VALUES
(1, 'Examen', 16.5, '2023-12-15', 2.0),
(1, 'TP', 18.0, '2023-11-20', 1.0),
(2, 'Examen', 14.0, '2023-12-15', 2.0),
(2, 'TP', 15.5, '2023-11-20', 1.0),
(3, 'Examen', 17.0, '2023-12-20', 2.0),
(4, 'Examen', 15.0, '2023-12-15', 2.0),
(4, 'TP', 16.0, '2023-11-20', 1.0),
(5, 'Examen', 18.5, '2023-12-20', 2.0),
(8, 'Examen', 12.0, '2022-12-20', 2.0),
(8, 'TP', 14.0, '2022-11-25', 1.0),
(9, 'Examen', 13.5, '2022-12-20', 2.0),
(10, 'Examen', 19.0, '2023-12-15', 2.0),
(10, 'Projet', 17.5, '2024-01-30', 1.5),
(11, 'Examen', 16.0, '2024-01-30', 2.0),
(12, 'Examen', 15.5, '2022-12-20', 2.0),
(13, 'Examen', 17.5, '2023-01-30', 2.0),
(15, 'Examen', 11.0, '2022-12-15', 2.0),
(15, 'Rattrapage', 13.0, '2023-01-20', 2.0),
(16, 'Examen', 18.0, '2023-01-30', 2.0),
(17, 'Examen', 16.5, '2023-12-15', 2.0);