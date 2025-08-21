> OK, we may assume that we managed to develop working datalake wharehouse for stooq daily data. We are pulling data from the web and making pradictions      
  about growth in seven days from now.
  Now we want to build a React web application displaying data we managed to collect and produce. For web app use data sets available from 
  prod_stock_data schema. We want to see visualizations explaining at what stock we are looking at, what is their history. What are the predictions 
  related to paricular stock. What says model about predictions of paricular stocks. What are the essentials informations about model for particular 
  model. Including it's parametrs, training times and so on. Add dark mode to the app. As for now allow to launch the app using docker desktop. The app       
  it self should live inside a dockerized enviroment which later on could serve as deployment to the cloud provider. Think about plan of how to develop       
  such web application based on our data. Save the plan to ./docs/knowledge_base. Remember that DDL for our schema is in @sql/schema_template.sql.j2 and      
  remember that you can pull some data rows using docker statments passing postgresql queries to the database to understand our data better