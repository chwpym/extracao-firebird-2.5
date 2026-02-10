-- ====================================
-- ÍNDICES PARA OTIMIZAÇÃO DO RELATÓRIO DE FATURAMENTO
-- ====================================
-- 
-- Este script cria índices estratégicos para melhorar
-- a performance das consultas de faturamento por cliente
--
-- Ganho esperado: 6-11 segundos → < 2 segundos
-- ====================================

-- PEDIDO (Cabeçalho de Venda)
-- Índice por cliente para filtrar rapidamente
CREATE INDEX IDX_PEDIDO_CLIENTE ON PEDIDO(CLI_CODIGO);

-- Índice por data para filtrar período (se não existir do Kardex)
CREATE INDEX IDX_PEDIDO_DATA ON PEDIDO(PED_DATAVENDA);

-- PEDITENS (Itens de Venda)
-- Índice por operação para JOIN com PEDIDO (se não existir do Kardex)
CREATE INDEX IDX_PEDITENS_PEDOP ON PEDITENS(PED_NUMEROOPERACAO);

-- RECEBER (Contas a Receber)
-- Índice por pedido para JOIN rápido
CREATE INDEX IDX_RECEBER_PEDIDO ON RECEBER(PED_NUMEROOPERACAO);

-- RECEBTO (Recebimentos/Quitações)
-- Índice por operação de receber para verificar pagamento
CREATE INDEX IDX_RECEBTO_RECOP ON RECEBTO(REC_NUMEROOPERACAO);

COMMIT;
