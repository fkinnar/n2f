-- En environnement de développement, on limite à 5 éléments par catégorie
-- afin de réduire le volume de données, accélérer les tests et éviter les
-- impacts de performance sur les environnements partagés.
WITH ranked AS (
  SELECT
    [typ]
      ,[client]
      ,[code]
      ,[description]
      ,[status]
      ,[date_from]
      ,[date_to]
      ,ROW_NUMBER() OVER (PARTITION BY [typ] ORDER BY [code]) AS rn
  FROM [AgrProd].[dbo].[iris_N2F_Analytics]
  WHERE
    ( [typ] = 'PROJECT' AND [code] LIKE 'P%' ) OR
    [typ] IN ('SUBPOST', 'PLAQUE')
)
SELECT
  [typ]
      ,[client]
      ,[code]
      ,[description]
      ,[status]
      ,[date_from]
      ,[date_to]
FROM ranked
WHERE rn <= 10
ORDER BY [typ], [code];