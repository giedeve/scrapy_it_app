# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import psycopg2
from decouple import config
from datetime import date

import hashlib
import random
from datetime import timedelta

from django.utils import timezone


# hashed_items_db = JobOffert.objects.filter(still_active = True)
# hashed_items_db = JobOffert.objects.all()
# hashed_list=[item.hash_id for item in hashed_items_db]

class ScrapyJobItPipeline:

    def open_spider(self, spider):
        hostname = 'localhost'
        username = config('USERNAME')
        password = config('PASSWORD')
        database = 'jobit'
        self.connection = psycopg2.connect(host=hostname, user=username, password=password, dbname=database)
        self.cur = self.connection.cursor()
        hashed_items_db = self.cur.execute("select * from job_offert where still_active='True'")
        hashed_list = [item.hash_id for item in hashed_items_db]

    def close_spider(self, spider):#TODO
        not_scrapped_items = JobOffert.objects.filter(scrapped=False, still_active=True, job_service=job_service)
        for item in not_scrapped_items:
            item.still_active = False
            item.end_date = timezone.now() - timedelta(days=1)
            item.save()
        scrapped_items = JobOffert.objects.filter(scrapped=True, job_service=job_service)
        for item in scrapped_items:
            item.scrapped = False
            item.save()
        return item
        self.cur.close()
        self.connection.close()

    def create_hash(self, *args):
        m = hashlib.md5()
        for arg in args:
            m.update(str(arg).replace("\n", "").encode('utf-8'))

        data = m.hexdigest()
        return data

    def process_item(self, item, spider, hashed_list):
        args = item['title'] + item['price_range'] + item['company'] + item['city']
        for k in item['keywords']:
            args = args + k
        hash_id = self.create_hash(args)
        # item['hash_id'] = hash_id
        if hash_id not in hashed_list:
            self.cur.execute(
                "INSERT INTO job_offert (title, salary_range, company, city,keywords, job_url, scrappy_date, scrapped, "
                "still_active, job_service, hash_id, open_date, end_date) VALUES (%s,%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"\
                ,(item['title'], item['salary_range'], item['company'], item['city'], item['keywords'], item['job_url'],
                  date.today(), item['scrapped'], item['still_active'], item['job_service'], hash_id, date.today(), None))
            # item['hash_id'] = hash_id
            # # item['scrapped'] = True
            # item.save()
        else:
            hashed_list.remove(hash_id)
            self.cur.execute('UPDATE job_offert SET scrapped=True WHERE hash_id=hash_id')
            # old_item = self.cur('select * from jobit_job_offert where hash_id=hash_id')
            #    # JobOffert.objects.get(hash_id=hash_id)
            # old_item.scrapped = True
            # old_item.save(update_fields=['scrapped'])
        self.connection.commit()
        return item
