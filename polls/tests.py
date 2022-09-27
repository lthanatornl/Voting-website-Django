from django.test import TestCase
from django.db import connection,transaction
    

# Create your tests here.
cursor = connection.cursor()

query = ''' SELECT  a.first_name + ' ' +a.last_name as f_l_name , b.candy_id,c.vote_id,c.vname
  FROM [PRvote].[dbo].[auth_user] a inner join [PRvote].[dbo].[polls_candidate] b  On a.id=b.candy_id inner join  [PRvote].[dbo].[polls_vvote] c
  On b.vvote_id=c.vote_id '''
  
query_list = build_query_list()
cursor.executemany(query, query_list)
transaction.commit()