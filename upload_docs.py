# 163865it [1:31:29, 29.85it/s]
import os
import logging
import pandas as pd
import sys
import json
from pprint import pprint
from dataclasses import asdict
from typing import Any, Callable, Dict, List, Union, Iterable, Mapping
sys.path.append('/home/dso/ed/ed-app/services/flask')

from tqdm import tqdm
from flask import Flask, logging as flask_logging, jsonify
from sqlalchemy.orm import contains_eager
from flask_sqlalchemy import SQLAlchemy

from app import create_app, config, models
from app.extensions import db

def get_register_app():
    
    db_config = {
        "host": "127.0.0.1",
        "port": "3306",
        "user": "admin",
        "password": "password",
        "database": "ed", 
    }

    db_user = db_config.get("user")
    db_pwd = db_config.get("password")
    db_host = db_config.get("host")
    db_port = db_config.get("port")
    db_name = db_config.get("database")

    db_connection_str = "mysql+pymysql://{}:{}@{}:{}/{}".format(
        db_user, db_pwd, db_host, db_port, db_name
    )

    app = create_app(config.Config)
    
    app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
        "ST_DATABASE_URI", db_connection_str
    )

    logging.getLogger("sqlalchemy.engine").setLevel(logging.ERROR)
    logging.getLogger("sqlalchemy.pool").setLevel(logging.ERROR)

    flask_logging.create_logger(app)

    return app

if __name__ == "__main__":

    app = get_register_app()
    db = SQLAlchemy(app)

    file = '/home/dso/ed/output_ner_full.jsonl'
    dat =[]
    with open(file,'r', encoding='utf-8') as j:
        for line in tqdm(j):   

            with app.app_context():

                # app.logger.info("Deleting Context table..")
                # models.Context.query.delete()
                # db.session.commit()
                # app.logger.info("Done")

                # app.logger.info("Deleting Entity table..")
                # models.Entity.query.delete()
                # db.session.commit()
                # app.logger.info("Done")

                # app.logger.info("Deleting Doc table..")
                # models.Doc.query.delete()
                # db.session.commit()
                # app.logger.info("Done")


                record = json.loads(line)

                # for record in tqdm(dat):

                doc_obj = models.Doc(csn = record.get('csn'),
                                    text = record.get('text'), 
                                    date = record.get('date')
                                    # internal_id = record.get('internal_id')
                                    )
                db.session.add(doc_obj)

                for entity in record['entities']:
                    ent_obj = models.Entity(csn = doc_obj.csn, 
                                            text = entity['entity_text'],
                                            start_char = entity.get('start_char'),
                                            end_char = entity.get('end_char'),
                                            is_negated = entity.get('is_negated'),
                                            is_uncertain = entity.get('is_uncertain'),
                                            is_historical = entity.get('is_historical'),
                                            is_hypothetical = entity.get('is_hypothetical'),
                                            is_family = entity.get('is_family'),
                                            sentence = entity.get('current_sentence_extracted'),
                                            section_category = entity.get('section_category'),
                                            section_title = entity.get('section_title'))
                    db.session.add(ent_obj)
                    db.session.flush()

                    if len(entity['modifiers']) > 0:
                        for modifier in entity['modifiers']:
                            mod_obj = models.Context(
                                ent_id = ent_obj.ent_id,
                                modifier_text = modifier.get('modifier_text'),
                                modifier_category = modifier.get('modifier_category'),
                                modifier_direction = modifier.get('modifier_direction'),
                                modifier_start_char = modifier.get('modifier_start_char') ,
                                modifier_end_char = modifier.get('modifier_end_char'),
                                modifier_scope_start_char = modifier.get('modifier_scope_start_char'),
                                modifier_scope_end_char = modifier.get('modifier_scope_end_char')
                            )
                        db.session.add(mod_obj)
                db.session.flush()
                db.session.commit()
            app.logger.info('Done')