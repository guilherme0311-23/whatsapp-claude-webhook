CREATE TABLE sessoes (
    id SERIAL PRIMARY KEY,
    remote_jid TEXT UNIQUE,
    criado_em TIMESTAMP
);

CREATE TABLE mensagens (
    id SERIAL PRIMARY KEY,
    sessao_id INTEGER REFERENCES sessoes(id),
    role TEXT,
    conteudo TEXT,
    criado_em TIMESTAMP
);