# 📖 Manual de Uso - Sistema de Extração Firebird 2.5

Este guia fornece instruções detalhadas sobre todas as funcionalidades do sistema, desde a configuração básica até o uso de ferramentas avançadas de diagnóstico.

---

## 🚀 1. Visão Geral

O sistema foi projetado para facilitar a migração de dados de bancos legados Firebird 2.5 para Excel. Ele oferece uma interface amigável, busca inteligente e ferramentas de validação de dados.

## ⚙️ 2. Configurações e Conexão

Para iniciar, preencha os campos na aba de configuração:

- **Banco de Dados (.FDB)**: Localize o arquivo de dados.
- **Client Library (fbclient.dll)**: Essencial para a comunicação com o Firebird.
- **Credenciais**: Geralmente `SYSDBA` e `masterkey`.

> [!IMPORTANT]
> Certifique-se de que a arquitetura da `fbclient.dll` (32 ou 64 bits) seja a mesma do seu Python.

## 📊 3. Extração para Migração

O fluxo de extração principal gera arquivos Excel para:

- Clientes (com tratamento inteligente de CPF/CNPJ).
- Produtos (catálogo completo).
- Fornecedores.
- Contas a Pagar e Receber.

### Tratamento do Cliente Moacir (Caso CPF com Espaços)

O sistema possui uma regra especial que usa `TRIM` e `NULLIF` no SQL para garantir que se um CPF estiver preenchido com espaços em branco, o sistema busque automaticamente o CNPJ, evitando campos vazios nos relatórios.

## 🛠️ 4. Central de Diagnóstico e Testes

Disponível em: **Ferramentas > Central de Diagnóstico e Testes**.
Esta tela permite executar scripts utilitários localizados na pasta `tools/`:

- **investigar_cliente.py**: Verificação profunda de documentos.
- **extrair_amostra_receber.py**: Gera um Excel rápido de 20 linhas para validação de layout.
- **teste_extracao_periodo.py**: Valida a extração em períodos específicos sem travar o banco.

## 📝 5. Editor SQL e Biblioteca

Disponível em: **Configurar > Editar Consultas SQL**.

- Use o dropdown para carregar queries pré-definidas.
- **Novas Queries de Diagnóstico**: Inserimos consultas para ver estrutura de tabelas e diagnosticar falhas de cadastro.
- **Placeholders**: Use `:DATA_INI` e `:DATA_FIM` para que o sistema substitua automaticamente pelas datas selecionadas na tela principal.

## 🎨 6. Temas e Estilo

O sistema suporta troca de temas em tempo real no menu **Temas**. Sua preferência é salva automaticamente para a próxima vez que abrir o app.

---

_Desenvolvido para Santa Fé Sistemas - Migração de Dados_
