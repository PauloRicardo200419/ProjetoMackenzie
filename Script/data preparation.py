import pandas as pd

# Caminhos dos arquivos Excel
caminho_base = r"C:\Users\paulo\Desktop\Projeto Faculdade\BD_Completa_DATASUS.csv"
caminho_municipios = r"C:\Users\paulo\Desktop\Projeto Faculdade\BD_Municipios.xlsx"

# Carregar os dados dos municípios
df_municipios = pd.read_excel(
    caminho_municipios,
    engine="openpyxl",
    usecols=["CÓDIGO DO MUNICÍPIO - IBGE", "MUNICÍPIO - IBGE", "UF"],
    dtype={"CÓDIGO DO MUNICÍPIO - IBGE": str}
)

# Carregar a base principal
df = pd.read_csv(
    caminho_base,
    delimiter=";",  # Define o separador como vírgula
    usecols=["DTOBITO", "CODMUNNATU", "DTNASC", "SEXO", "RACACOR", "LOCOCOR", "CODMUNOCOR", "ASSISTMED", "CIRCOBITO"],
    dtype={"CODMUNNATU": str, "CODMUNOCOR": str},
    #nrows=50  # Limitando para rodar mais rápido
)

# Formatar datas
# Garantir que os valores estão como strings e remover espaços em branco
df["DTOBITO"] = df["DTOBITO"].astype(str).str.strip()
df["DTNASC"] = df["DTNASC"].astype(str).str.strip()

# Converter para datetime e manter as datas válidas
df["DTOBITO"] = pd.to_datetime(df["DTOBITO"], format="%d/%m/%Y", errors="coerce")
df["DTNASC"] = pd.to_datetime(df["DTNASC"], format="%d/%m/%Y", errors="coerce")

# Renomear coluna do DF de municípios para facilitar o merge
df_municipios.rename(columns={"CÓDIGO DO MUNICÍPIO - IBGE": "CODMUN"}, inplace=True)

# Realizar o LEFT JOIN duas vezes para obter a descrição do município para CODMUNNATU e CODMUNOCOR
df_resultado = df.merge(df_municipios, left_on="CODMUNNATU", right_on="CODMUN", how="left") \
                 .rename(columns={"MUNICÍPIO - IBGE": "MUNICIPIO_NATU", "UF": "UF_NATU"}) \
                 .drop(columns=["CODMUN"])

df_resultado = df_resultado.merge(df_municipios, left_on="CODMUNOCOR", right_on="CODMUN", how="left") \
                           .rename(columns={"MUNICÍPIO - IBGE": "MUNICIPIO_OCOR", "UF": "UF_OCOR"}) \
                           .drop(columns=["CODMUN"])
# Tratando Sexo
sexo_dict = {
    0: "Ignorado",
    1: "Masculino",
    2: "Feminino"
}

df_resultado["SEXO_DESC"] = df_resultado["SEXO"].map(sexo_dict)

#Tratando Racacor
racacor_dict = {
    1: "Branca",
    2: "Preta",
    3: "Amarela",
    4: "Parda",
    5: "Indígena",
    9: "Ignorado",
    None: "Ignorado"
}

df_resultado["RACACOR_DESC"] = df_resultado["RACACOR"].map(racacor_dict)

#Tratando Lococor
lococor_dict = {
    1: "Hospital",
    2: "Outro Estab. Saúde",
    3: "Domicílio",
    4: "Via Pública",
    5: "Outros",
    9: "Ignorado",
    None: "Ignorado"
}

df_resultado["LOCOCOR_DESC"] = df_resultado["LOCOCOR"].map(lococor_dict)

#Tratando Assistmed
assistmed_dict = {
    1: "Com assitência",
    2: "Sem assistência",
    9: "Ignorado",
    None: "Ignorado"
}

df_resultado["ASSISTMED_DESC"] = df_resultado["ASSISTMED"].map(assistmed_dict)

#Tratando Circobito
circobito_dict = {
    1: "Acidente",
    2: "Suicídio",
    3: "Homicídio",
    4: "Outros",
    9: "Ignorado",
    None: "Ignorado"
}

df_resultado["CIRCOBITO_DESC"] = df_resultado["CIRCOBITO"].map(circobito_dict)

#Criando colunas dos anos
df_resultado["ANO_NASC"] = df_resultado["DTNASC"].dt.year.astype("Int64")
df_resultado["ANO_OBITO"] = df_resultado["DTOBITO"].dt.year.astype("Int64")

#Criando colunas dos meses
df_resultado["MES_OBITO"] = df_resultado["DTOBITO"].dt.strftime("%B")

#Calculando idade
df_resultado["IDADE"] = df_resultado["ANO_OBITO"] - df_resultado["ANO_NASC"]

#Filtros
df_resultado = df_resultado[
    (df_resultado["UF_OCOR"] == "SP") & 
    (df_resultado["CIRCOBITO_DESC"] != "Ignorado") & 
    (df_resultado["CIRCOBITO_DESC"] != "Outros") & 
    (df_resultado["DTNASC"].notna())
]

#Aviso
print("Base 100% Tratada, iniciando exportação")

#Exibir as primeiras linhas do resultado
#print(df_resultado.head())

#Gera arquivo excel
caminho_saida = r"C:\Users\paulo\Desktop\Projeto Faculdade\base_tratada_python.xlsx"
df_resultado.to_excel(caminho_saida, index=False, engine="openpyxl")
print("Arquivo Gerado !!")