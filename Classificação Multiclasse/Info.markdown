# Projeto SEMANTIX

Este documento contém informações gerais sobre o projeto parceria Semantix desenvolvido ao longo do curso Cientista de Dados da EBAC.


O projeto segue a metodologia CRISP-DM, sendo subdividido em:

* Entendimento do negócio
* Entendimento dos dados
* Preparação dos dados
* Modelagem
* Avaliação do modelo

---

### Objetivo:

Suponha que uma empresa multinacional na área de motocicletas tenha interesse no mercado de um determinado país. Uma das analises será entender (e prever) as categorias das motocicletas com base na produção (ou importação) de peças deste país para criar uma estratégia de quais modelos
da marca são mais adequados para o perfil dos motociclistas deste país.

Contruír um modelo de classificação multiclasse que classifique categorias de motocicletas a partir de dados relacionados a peças e especificações técnicas.

---

### Coleta, Modelagem e Conclusões:

A coleta de dados foi feita via Kaggle, uma comunidade voltada a ciência de dados que também serve como repositório de diversas bases de dados públicas.

link:https://www.kaggle.com/datasets/emmanuelfwerr/motorcycle-technical-specifications-19702022

Para a modelagem, comparamos métricas de diferentes modelos de classificação multiclasse. O modelo final, que se apresentou mais adequado para o conjunto de dados, foi o Random Forest Classifier.

Após o desenvolvimento das etapas validamos o modelo em uma base de teste, obtendo boas métricas de avaliação, comprovamos a efetividade do modelo em classificar (e diferenciar) diferentes categorias de motocicletas, concluíndo assim o objetivo inicial do projeto.