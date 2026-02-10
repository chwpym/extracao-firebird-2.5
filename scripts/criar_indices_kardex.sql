-- ====================================
-- ÍNDICES PARA OTIMIZAÇÃO DO KARDEX
-- ====================================
-- 
-- Este script cria índices estratégicos para melhorar
-- a performance das consultas de movimentações (Kardex)
--
-- Ganho esperado: 3-5 segundos → < 1 segundo
-- ====================================

-- PEDITENS (Itens de Venda)
-- Índice por produto para filtrar rapidamente
CREATE INDEX IDX_PEDITENS_PROD ON PEDITENS(PROD_CODIGO);

-- Índice por operação para JOIN com PEDIDO
CREATE INDEX IDX_PEDITENS_PEDOP ON PEDITENS(PED_NUMEROOPERACAO);

-- PEDIDO (Cabeçalho de Venda)
-- Índice por data para filtrar período
CREATE INDEX IDX_PEDIDO_DATA ON PEDIDO(PED_DATAVENDA);

-- ENTITENS (Itens de Entrada/Compra)
-- Índice por produto para filtrar rapidamente
CREATE INDEX IDX_ENTITENS_PROD ON ENTITENS(PROD_CODIGO);

-- Índice por operação para JOIN com ENTRADA
CREATE INDEX IDX_ENTITENS_ENTOP ON ENTITENS(ENT_NUMEROOPERACAO);

-- ENTRADA (Cabeçalho de Entrada/Compra)
-- Índice por data para filtrar período
CREATE INDEX IDX_ENTRADA_DATA ON ENTRADA(ENT_DATAENTRADA);

COMMIT;
