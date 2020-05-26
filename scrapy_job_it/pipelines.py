# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
import psycopg2
from decouple import config
from datetime import date, timedelta

import hashlib
import random

from django.utils import timezone

# hashed_items_db = JobOffert.objects.filter(still_active = True)
# hashed_items_db = JobOffert.objects.all()
# hashed_list=[item.hash_id for item in hashed_items_db]
# hostname = 'localhost'
# username = 'postgres'
# # config('USERNAME')
# password = 'coderslab'
# # config('PASSWORD')
# database = 'jobit'
# connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
DATABASE_URL = os.environ['DATABASE_URL']
connection = psycopg2.connect(DATABASE_URL, sslmode='require')
cur = connection.cursor()
cur.execute("select array(select hash_id from job_offert where still_active=True)")
hashed_list = cur.fetchall()[0][0]
print(hashed_list)


# if hashed_items_db is not None:
#     hashed_list = [item['hash_id'] for item in hashed_items_db]
# else:
#     hashed_list = None

class ScrapyJobItPipeline:

    def open_spider(self, spider):
        # hostname = 'localhost'
        # username = 'postgres'
        # password = config('PASSWORD')
        # database = 'jobit'
        # self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        DATABASE_URL = os.environ['DATABASE_URL']
        self.connection = psycopg2.connect(DATABASE_URL, sslmode='require')
        self.cur = self.connection.cursor()

    def close_spider(self, spider):

        # aktualizacja nie skrapowanych ofert by je zamknąć - end date
        close_date = date.today() - timedelta(days=1)
        self.cur.execute(f"UPDATE job_offert SET end_date = '{close_date}', still_active=False FROM "
                         "(select * from job_offert where still_active=True and scrapped=False) t "
                         "WHERE t.hash_id=job_offert.hash_id")
        # zmiana scrapped na False na kolejne scrapowanie
        self.cur.execute(
            'UPDATE job_offert SET scrapped=False FROM (select * from job_offert where scrapped=TRUE) t  WHERE t.hash_id=job_offert.hash_id')
        self.connection.commit()
        self.cur.close()
        self.connection.close()

    def create_hash(self, *args):
        m = hashlib.md5()
        for arg in args:
            m.update(str(arg).replace("\n", "").encode('utf-8'))
        data = m.hexdigest()
        return data

    def process_item(self, item, spider):
        args = item['title'] + item['salary_range'] + item['company'] + item['city'] + item['job_url']
        for k in item['keywords']:
            args = args + k
        hash_id = self.create_hash(args)
        # poniżej pierwsze scrapowanie dla bazy danych
        # self.cur.execute(
        #     "INSERT INTO job_offert (title, salary_range, company, city,keywords, job_url, scrappy_date, scrapped, "
        #     "still_active, job_service, hash_id, open_date, end_date) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
        #     , (item['title'], item['salary_range'], item['company'], item['city'], item['keywords'], item['job_url'],
        #        date.today(), item['scrapped'], item['still_active'], item['job_service'], hash_id, date.today(), None))
        if hash_id not in hashed_list:
            #print('ZAPIS NOWEGO')
            try:
                self.cur.execute(
                    "INSERT INTO job_offert (title, salary_range, company, city,keywords, job_url, scrappy_date, scrapped, "
                    "still_active, job_service, hash_id, open_date, end_date) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)" \
                    ,
                    (item['title'], item['salary_range'], item['company'], item['city'], item['keywords'], item['job_url'],
                     date.today(), item['scrapped'], item['still_active'], item['job_service'], hash_id, date.today(),
                     None))
            except Exception as err:
                pass
        else:
            print('ROBIMY UPDATE')
            hashed_list.remove(hash_id)
            self.cur.execute('UPDATE job_offert SET scrapped=True WHERE hash_id=hash_id')
        self.connection.commit()
        return item
