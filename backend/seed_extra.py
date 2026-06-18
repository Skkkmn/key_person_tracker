import pymysql, datetime, random
c = pymysql.connect(host='localhost', user='root', password='wang97976', database='key_person_mgmt', charset='utf8mb4')
cu = c.cursor()
r = random.Random(99)
now = datetime.datetime.now()

cu.execute('SELECT person_id, name, address FROM key_person')
persons = cu.fetchall()
print(f'Persons: {len(persons)}')

cu.execute('SELECT COUNT(*) FROM lost_contact_track')
if cu.fetchone()[0] == 0:
    selected = r.sample(persons, min(5, len(persons)))
    for pid, name, addr in selected:
        lost_date = now - datetime.timedelta(days=r.randint(5, 45))
        resolved = r.random() > 0.5
        sql = '''INSERT INTO lost_contact_track 
            (person_id, lost_time, last_location, search_measures, family_contact, progress, status, resolved_at, created_at) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)'''
        cu.execute(sql, (
            pid, lost_date,
            r.choice(['火车站候车室', '长途汽车站', '城郊结合部', '小区附近', '某宾馆']),
            r.choice(['已调取监控，正在排查', '已联系家属，发布协查通报', '已组织警力在周边搜寻']),
            r.choice(['父亲:13800138100', '母亲:13800138200', '配偶:13800138300']),
            r.choice(['正在排查监控视频', '已锁定最后出现区域', '已找到，正在带回']),
            'resolved' if resolved else 'tracking',
            now - datetime.timedelta(days=r.randint(1, 10)) if resolved else None,
            lost_date,
        ))
    c.commit()
    print('Lost contacts added: 5')
else:
    print('Lost contacts already exist')

cu.execute('SELECT COUNT(*) FROM visit_task')
total_tasks = cu.fetchone()[0]
print(f'Total tasks: {total_tasks}')

cu.execute('SELECT COUNT(*) FROM visit_record')
vr_count = cu.fetchone()[0]
print(f'Existing visit records: {vr_count}')

if vr_count < 15:
    cu.execute('SELECT task_id, person_id FROM visit_task WHERE status="completed"')
    tasks = cu.fetchall()
    added = 0
    for tid, pid in tasks:
        if added >= 10:
            break
        vr_time = now - datetime.timedelta(days=r.randint(1, 30))
        cu.execute('''INSERT INTO visit_record 
            (task_id, person_id, visitor_id, visit_time, location, content, performance, thought_dynamics, life_difficulty, has_abnormality, photo_urls) 
            VALUES (%s, %s, 1, %s, %s, %s, %s, %s, %s, %s, '[]')''',
            (tid, pid, vr_time, '走访地址',
             f'走访记录内容 - {random.choice(["稳定","良好","正常","有异常"])}',
             r.choice(['良好', '一般', '良好', '较差']),
             r.choice(['思想稳定', '情绪平稳', '略显焦虑']),
             r.choice(['无', '经济困难', '就业困难']),
             r.random() < 0.2))
        added += 1
    c.commit()
    print(f'Visit records added: {added}')
else:
    print('Visit records already sufficient')

cu.execute('SELECT COUNT(*) FROM risk_assessment')
ra_count = cu.fetchone()[0]
print(f'Risk assessments: {ra_count}')

cu.execute('SELECT COUNT(*) FROM notification')
nf_count = cu.fetchone()[0]
print(f'Notifications: {nf_count}')

cu.execute('SELECT COUNT(*) FROM person_alert')
pa_count = cu.fetchone()[0]
print(f'Person alerts: {pa_count}')

c.close()
print('Done!')
