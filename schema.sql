CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome VARCHAR(100) NOT NULL UNIQUE,
    senha VARCHAR(200) NOT NULL
);

CREATE TABLE romaneio (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    identificacao_animal VARCHAR(50) NOT NULL,
    raca VARCHAR(50) NOT NULL,
    peso_kg REAL NOT NULL CHECK (peso_kg > 0 AND peso_kg <= 2000),
    data_pesagem DATE NOT NULL,
    observacoes VARCHAR(300)
);

CREATE TRIGGER validar_peso_romaneio
BEFORE INSERT ON romaneio
FOR EACH ROW
WHEN NEW.peso_kg <= 0 OR NEW.peso_kg > 2000
BEGIN
    SELECT RAISE(ABORT, 'Peso inválido.');
END;

CREATE INDEX idx_romaneio_data ON romaneio(data_pesagem);
