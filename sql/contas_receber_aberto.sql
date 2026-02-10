-- CONTAS A RECEBER EM ABERTO (MODELO EXCEL OTIMIZADO)
SELECT 
    '1' AS "Empresa",
    r.REC_NUMEROPEDIDO AS "Número da Duplicata",
    r.REC_NUMERONOTAFISCAL AS "Número da NF",
    r.CLI_CODIGO AS "Código do Cliente",
    COALESCE(NULLIF(TRIM(c.CLI_CPF), ''), NULLIF(TRIM(c.CLI_CNPJ), '')) AS "CNPJ/CPF",
    c.CLI_NOME AS "Descrição do Cliente",

    d.RED_PARCELA AS "Parcela da Duplicata",
    r.REC_DATAEMISSAO AS "Data de Movimento",
    d.RED_DATAVENCIMENTO AS "Data de Vencimento",
    d.RED_VALORPARCELA AS "Valor da Duplicata",
    '' AS "Ocorrência",
    COALESCE(ult_rec.TPF_SIGLA, '') AS "Forma de Pagamento",
    COALESCE(ult_rec.REB_DESCONTO, 0) AS "Desconto",
    COALESCE(ult_rec.REB_JUROS + COALESCE(ult_rec.REB_MULTA, 0), 0) AS "Valor Juros Cobrado",
    0 AS "% Juros Mora Diário",
    d.RED_VALORRECEBIDO AS "Valor Pago",
    ult_rec.REB_DATARECEBIMENTO AS "Data de Pagamento",
    d.RED_NUMEROBOLETO AS "Nosso Número",
    r.REC_HISTORICO AS "Histórico"
FROM RECDET d
JOIN RECEBER r ON d.REC_NUMEROOPERACAO = r.REC_NUMEROOPERACAO
LEFT JOIN CLIENTE c ON c.CLI_CODIGO = r.CLI_CODIGO
LEFT JOIN (
    -- Busca o último pagamento da parcela para pegar detalhes
    SELECT 
        rt.REC_NUMEROOPERACAO, 
        rt.RED_PARCELA, 
        MAX(rt.REB_DATARECEBIMENTO) as REB_DATARECEBIMENTO,
        MAX(rt.TPF_SIGLA) as TPF_SIGLA,
        SUM(rt.REB_DESCONTO) as REB_DESCONTO,
        SUM(rt.REB_JUROS) as REB_JUROS,
        SUM(rt.REB_MULTA) as REB_MULTA
    FROM RECEBTO rt
    GROUP BY rt.REC_NUMEROOPERACAO, rt.RED_PARCELA
) ult_rec ON ult_rec.REC_NUMEROOPERACAO = d.REC_NUMEROOPERACAO AND ult_rec.RED_PARCELA = d.RED_PARCELA
WHERE (d.RED_VALORRECEBIDO < d.RED_VALORPARCELA)
  AND :CAMPO_DATA BETWEEN :DATA_INI AND :DATA_FIM
ORDER BY :CAMPO_DATA
