import pymysql, datetime, random, json
c = pymysql.connect(host='localhost', user='root', password='wang97976', database='key_person_mgmt', charset='utf8mb4')
cu = c.cursor()
r = random.Random(123)
now = datetime.datetime.now()

cu.execute('SELECT COUNT(*) FROM operation_log')
count = cu.fetchone()[0]
print(f'Existing logs: {count}')

if count > 0:
    print('Already has data')
else:
    cu.execute('SELECT person_id, name FROM key_person')
    persons = {p[0]: p[1] for p in cu.fetchall()}

    cu.execute('SELECT alert_id, person_id, alert_type FROM person_alert')
    alerts = cu.fetchall()

    cu.execute('SELECT task_id, person_id FROM visit_task')
    tasks = cu.fetchall()

    cu.execute('SELECT record_id, person_id FROM visit_record')
    records = cu.fetchall()

    cu.execute('SELECT assessment_id, person_id FROM risk_assessment')
    assessments = cu.fetchall()

    cu.execute('SELECT track_id, person_id FROM lost_contact_track')
    tracks = cu.fetchall()

    log_data = []

    for pid, name in list(persons.items())[:10]:
        log_data.append((1, 'admin', 'CREATE', 'key_person', pid, name, 'null', json.dumps({'name': name}, ensure_ascii=False), now - datetime.timedelta(days=r.randint(30, 60))))

    for pid, name in list(persons.items())[:5]:
        log_data.append((1, 'admin', 'UPDATE', 'key_person', pid, name, json.dumps({'risk_level': 'low'}), json.dumps({'risk_level': 'medium'}), now - datetime.timedelta(days=r.randint(15, 35))))

    for aid, pid, atype in alerts[:10]:
        pname = persons.get(pid, '')
        log_data.append((1, 'admin', 'CREATE', 'alert', aid, f'{pname}-{atype}', 'null', json.dumps({'alert_type': atype}, ensure_ascii=False), now - datetime.timedelta(days=r.randint(1, 20))))

    for tid, pid in tasks[:10]:
        pname = persons.get(pid, '')
        log_data.append((1, 'admin', 'CREATE', 'visit_task', tid, f'{pname}-走访任务', 'null', json.dumps({'title': '走访任务'}), now - datetime.timedelta(days=r.randint(3, 30))))

    for rid, pid in records:
        pname = persons.get(pid, '')
        log_data.append((1, 'admin', 'CREATE', 'visit_record', rid, f'走访记录-{pname}', 'null', json.dumps({'has_abnormality': False}), now - datetime.timedelta(days=r.randint(1, 15))))

    for aid, pid in assessments[:15]:
        pname = persons.get(pid, '')
        log_data.append((1, 'admin', 'CREATE', 'risk_assessment', aid, f'风险评估-{pname}', 'null', json.dumps({'score': 70}), now - datetime.timedelta(days=r.randint(1, 45))))

    for tid, pid in tracks:
        pname = persons.get(pid, '')
        log_data.append((1, 'admin', 'CREATE', 'lost_contact', tid, f'失联台账-{pname}', 'null', json.dumps({'status': 'tracking'}), now - datetime.timedelta(days=r.randint(3, 30))))

    log_data.append((1, 'admin', 'ARCHIVE', 'key_person', 5, '孙丽', 'null', json.dumps({'archived': True}), now - datetime.timedelta(days=20)))
    log_data.append((1, 'admin', 'MARK_LOST', 'key_person', 20, '韩磊', 'null', json.dumps({'control_status': 'lost'}), now - datetime.timedelta(days=25)))
    log_data.append((1, 'admin', 'STATUS_CHANGE', 'key_person', 10, '刘洋', json.dumps({'control_status': 'monitored'}), json.dumps({'control_status': 'lost'}), now - datetime.timedelta(days=12)))

    sql = 'INSERT INTO operation_log (user_id,username,action,entity_type,entity_id,entity_name,old_value,new_value,ip_address,created_at) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
    for uid, uname, action, etype, eid, ename, oldv, newv, ts in log_data:
        cu.execute(sql, (uid, uname, action, etype, eid, ename, oldv, newv, '127.0.0.1', ts))

    c.commit()
    print(f'Inserted {len(log_data)} logs')

c.close()
print('Done')
