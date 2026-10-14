# 🛒 PDV — Artigos Religiosos

Sistema completo de Ponto de Venda desenvolvido para lojas de artigos religiosos, esotéricos e místicos. Interface web moderna com backend robusto em Python e banco de dados MySQL.

---

## ✨ Funcionalidades

- **PDV completo** — leitor de código de barras plug & play, múltiplas formas de pagamento (dinheiro, PIX, débito, crédito, pontos)
- **Dashboard em tempo real** — vendas do dia, ticket médio, alertas de estoque, atualização automática a cada 30s
- **Programa de fidelidade** — acúmulo de pontos por compra + voucher de R$50 a cada 10 compras
- **Orçamentos** — criação, aprovação, recusa, conversão em venda e impressão em PDF profissional
- **Notas Fiscais** — emissão automática de NF em PDF ao finalizar cada venda
- **Relatórios** — vendas por período, produtos mais vendidos e posição de estoque com download em PDF
- **Gestão de estoque** — alertas automáticos de estoque baixo/zerado, geração de código de barras automática
- **Cadastro de clientes** — histórico de compras, saldo de pontos e vouchers disponíveis
- **Gestão de usuários** — perfis de Administrador e Funcionário com controle de acesso
- **Módulo SEFAZ-PI** — pronto para ativação ao obter certificado digital (NFC-e)

---

## 🛠 Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.13 + Django 4.2 + Django REST Framework |
| Banco de Dados | MySQL 8.0 |
| Frontend | React 18 + Vite + CSS puro |
| Autenticação | JWT (djangorestframework-simplejwt) |
| PDFs | ReportLab |
| Código de Barras | python-barcode (Code128) |
| CORS | django-cors-headers |

---

## 📁 Estrutura do Projeto

```
pdv-artigos-religiosos/
├── backend/
│   ├── apps/
│   │   ├── accounts/      # Usuários e clientes
│   │   ├── products/      # Produtos e categorias
│   │   ├── pdv/           # Caixa e vendas
│   │   ├── quotations/    # Orçamentos
│   │   ├── invoices/      # Notas fiscais
│   │   ├── loyalty/       # Programa de fidelidade
│   │   ├── dashboard/     # Dados em tempo real
│   │   └── reports/       # Relatórios e PDFs
│   ├── flor_dende/        # Configurações Django
│   ├── .env.example       # Modelo de configuração
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── pages/         # Dashboard, PDV, Produtos...
│   │   ├── components/    # Sidebar, Navbar, Modais
│   │   ├── api/           # Axios + interceptors JWT
│   │   └── styles/        # CSS global
│   └── package.json
├── iniciar.bat            # Inicia o sistema (Windows)
├── instalar.bat           # Instala dependências
└── banco.sql              # Script de criação do banco
```

---

## 🚀 Como instalar e rodar

### Pré-requisitos
- Python 3.11+ — [python.org](https://python.org)
- Node.js 18+ — [nodejs.org](https://nodejs.org)
- MySQL 8.0+ — [mysql.com](https://mysql.com)

### 1. Clone o repositório
```bash
git clone https://github.com/SEU_USUARIO/pdv-artigos-religiosos.git
cd pdv-artigos-religiosos
```

### 2. Crie o banco de dados no MySQL
```sql
CREATE DATABASE pdv_artigos CHARACTER SET utf8mb4;
CREATE USER 'pdv_user'@'localhost' IDENTIFIED BY 'SuaSenha';
GRANT ALL PRIVILEGES ON pdv_artigos.* TO 'pdv_user'@'localhost';
FLUSH PRIVILEGES;
```

### 3. Configure o ambiente
```bash
cp backend/.env.example backend/.env
# Edite o backend/.env com suas credenciais
```

### 4. Instale (Windows)
```
Duplo clique em instalar.bat
```

Ou manualmente:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
cd ../frontend
npm install
```

### 5. Inicie o sistema
```
Duplo clique em iniciar.bat
```

Ou manualmente em dois terminais:
```bash
# Terminal 1 — Backend
cd backend && venv\Scripts\activate && python manage.py runserver

# Terminal 2 — Frontend
cd frontend && npm run dev
```

Acesse: **http://localhost:5173**

---

## ⚙️ Variáveis de Ambiente

Copie `backend/.env.example` para `backend/.env` e configure:

| Variável | Descrição | Padrão |
|---|---|---|
| `SECRET_KEY` | Chave secreta Django | — (obrigatório) |
| `DB_PASSWORD` | Senha do MySQL | — (obrigatório) |
| `PONTOS_POR_REAL` | Pontos acumulados por R$1 | `1` |
| `COMPRAS_PARA_VOUCHER` | Compras para ganhar voucher | `10` |
| `VALOR_VOUCHER` | Valor do voucher em R$ | `50` |

---

## 🔐 Segurança

- Senhas criptografadas com PBKDF2 + SHA256
- Autenticação via JWT com refresh token e blacklist
- Arquivo `.env` nunca commitado no repositório
- CORS configurado para aceitar apenas origens autorizadas

---

## 📄 Licença

Este projeto é proprietário. Todos os direitos reservados.  
Para licenciamento e uso comercial, entre em contato.

---

Desenvolvido por **[Pablo Ataide]** — 2026