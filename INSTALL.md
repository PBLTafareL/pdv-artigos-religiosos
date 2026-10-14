# 🌸 Flor de Dendê PDV — Instalação

## Pré-requisitos
- Python 3.11+ em https://python.org
- Node.js 18+ em https://nodejs.org
- MySQL 8.0+ rodando na porta 3306

## Passos

### 1. Criar banco de dados
Abra o MySQL Workbench e execute o arquivo `banco.sql`

### 2. Instalar o sistema
Dê duplo clique em **instalar.bat**
(cria o venv, instala dependências, roda migrations e cria superusuário)

### 3. Usar o sistema
Dê duplo clique em **iniciar.bat**
Acesse: http://localhost:5173

## Credenciais padrão do banco (.env)
- DB: flor_dende_pdv
- Usuário: flor_dende_user
- Senha: FlorDende_2026!

## Dicas
- Login: use e-mail ou nome de usuário
- Leitor de código de barras: plug & play (USB HID)
- SEFAZ-PI: módulo pronto, ativar após obter certificado
