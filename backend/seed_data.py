from datetime import datetime, timedelta
import random

from app import create_app
from app.extensions import db
from app.models.key_person import KeyPerson
from app.models.person_alert import PersonAlert
from app.models.visit_task import VisitTask
from app.models.visit_record import VisitRecord
from app.models.risk_assessment import RiskAssessment
from app.models.notification import Notification
from app.models.lost_contact_track import LostContactTrack
from app.models.department import Department
from app.models.person_category import PersonCategory

app = create_app()
rand = random.Random(42)

def rdate(days_ago):
    return datetime.now() - timedelta(
        days=rand.randint(0, days_ago),
        hours=rand.randint(0, 23),
        minutes=rand.randint(0, 59)
    )

with app.app_context():
    if Department.query.count() <= 1:
        depts = [
            Department(dept_name='城南派出所', dept_code='CNPCS', parent_id=1, address='城南区解放路1号', phone='0510-88880001'),
            Department(dept_name='城北派出所', dept_code='CBPCS', parent_id=1, address='城北区建设路2号', phone='0510-88880002'),
            Department(dept_name='刑侦大队', dept_code='XZDD', parent_id=1, address='刑侦大楼', phone='0510-88880010'),
            Department(dept_name='治安大队', dept_code='ZADD', parent_id=1, address='治安大楼', phone='0510-88880020'),
            Department(dept_name='指挥中心', dept_code='ZHZX', parent_id=1, address='指挥大楼', phone='0510-88880000'),
        ]
        for d in depts:
            if not Department.query.filter_by(dept_code=d.dept_code).first():
                db.session.add(d)
        db.session.commit()
        print('Departments added')

    if PersonCategory.query.count() <= 1:
        cats = [
            PersonCategory(category_name='涉恐人员', category_code='SK', description='涉恐重点关注对象'),
            PersonCategory(category_name='涉稳人员', category_code='SW', description='涉稳重点关注对象'),
            PersonCategory(category_name='严重精神障碍患者', category_code='JS', description='严重精神障碍患者'),
            PersonCategory(category_name='刑事解教人员', category_code='XS', description='刑事解教重点人员'),
            PersonCategory(category_name='吸毒人员', category_code='XD', description='吸毒重点管控对象'),
            PersonCategory(category_name='重点上访人员', category_code='SF', description='重点上访人员'),
            PersonCategory(category_name='其他重点人员', category_code='QT', description='其他重点关注对象'),
        ]
        for c in cats:
            if not PersonCategory.query.filter_by(category_code=c.category_code).first():
                db.session.add(c)
        db.session.commit()
        print('Categories added')

    if KeyPerson.query.count() <= 1:
        dept_ids = [d.dept_id for d in Department.query.all()]
        persons_data = [
            ('张强','男','320101198503121234','1985-03-12','13800138001','城南区中山路12号','城南区中山路12号',3,'high','曾参与非法集会，有暴力倾向','无业'),
            ('李伟','男','320101198807151234','1988-07-15','13800138002','城北区人民路8号','城北区人民路8号',4,'medium','刑满释放人员，盗窃前科','临时工'),
            ('王芳','女','320101199203201234','1992-03-20','13800138003','城南区花园路3号','城南区花园路3号',2,'high','涉恐嫌疑，有境外联系记录','无业'),
            ('赵强','男','320101197511081234','1975-11-08','13800138004','城北区新村15号','城北区新村15号',5,'medium','多次吸毒被查，社区戒毒中','快递员'),
            ('孙丽','女','320101198901252345','1989-01-25','13800138005','开发区科技路6号','开发区科技路6号',6,'low','多次赴京上访记录','无业'),
            ('周明','男','320101198206181234','1982-06-18','13800138006','滨湖区太湖路9号','滨湖区太湖路9号',3,'medium','精神分裂症病史，近期停药','无业'),
            ('吴杰','男','320101199512011234','1995-12-01','13800138007','新城区长江路22号','新城区长江路22号',3,'high','涉恐网上传播极端思想','个体户'),
            ('郑红','女','320101197808301234','1978-08-30','13800138008','老城区解放路5号','老城区解放路5号',7,'low','一般关注','退休'),
            ('陈浩','男','320101199001121234','1990-01-12','13800138009','城南区湖滨路7号','城南区湖滨路7号',4,'medium','抢劫前科，刚出狱3个月','无业'),
            ('刘洋','男','320101198412221234','1984-12-22','13800138010','城北区车站路1号','城北区车站路1号',5,'high','复吸风险高，多次强戒','无业'),
            ('黄婷','女','320101199308151234','1993-08-15','13800138011','开发区创业路88号','开发区创业路88号',2,'medium','涉恐家属，需定期走访','公司职员'),
            ('林军','男','320101198701051234','1987-01-05','13800138012','滨湖区山水东路11号','滨湖区山水东路11号',6,'medium','多次上访，近期情绪激动','农民'),
            ('何敏','女','320101199609231234','1996-09-23','13800138013','新城区黄山南路3号','新城区黄山南路3号',3,'low','精神异常轻度，有监护人','无业'),
            ('马超','男','320101198011301234','1980-11-30','13800138014','老城区和平路19号','老城区和平路19号',4,'high','多次暴力犯罪，重点关注','无业'),
            ('高洁','女','320101199111111234','1991-11-11','13800138015','城南区向阳村5组','城南区向阳村5组',5,'medium','社区戒毒中','服务员'),
            ('罗刚','男','320101197603051234','1976-03-05','13800138016','城北区北大街33号','城北区北大街33号',7,'low','一般关注对象','工人'),
            ('梁燕','女','320101198806091234','1988-06-09','13800138017','开发区科技园2栋','开发区科技园2栋',2,'medium','境外关系复杂','翻译'),
            ('宋涛','男','320101199407211234','1994-07-21','13800138018','滨湖区雪浪街道12号','滨湖区雪浪街道12号',6,'high','极端上访倾向','自由职业'),
            ('唐静','女','320101198310171234','1983-10-17','13800138019','新城区龙山路99号','新城区龙山路99号',3,'low','精神异常稳定期','会计'),
            ('韩磊','男','320101197912081234','1979-12-08','13800138020','老城区建设巷6号','老城区建设巷6号',5,'high','复吸高风险，脱管状态','无业'),
        ]
        for name, gender, id_card, birth, phone, addr, current, cat_id, risk, case_desc, emp in persons_data:
            person = KeyPerson(
                name=name, gender=gender, id_card=id_card, birth_date=birth,
                phone=phone, address=addr, current_address=current,
                category_id=cat_id, risk_level=risk,
                department_id=rand.choice(dept_ids),
                case_description=case_desc, employment_status=emp,
                control_status='monitored',
                education=rand.choice(['小学','初中','高中','大专','本科']),
                political_status=rand.choice(['群众','党员','共青团员']),
                ethnicity=rand.choice(['汉族','回族','壮族']),
                marital_status=rand.choice(['未婚','已婚','离异']),
                household_type=rand.choice(['城镇','农村']),
                employer=emp if emp not in ('无业','退休') else None,
            )
            db.session.add(person)
        db.session.commit()
        print(f'Key persons: {len(persons_data)} added')
    else:
        print('Key persons: skipped')

    persons = KeyPerson.query.all()
    print(f'Total persons: {len(persons)}')

    if VisitTask.query.count() <= 1:
        statuses = ['pending', 'in_progress', 'completed', 'cancelled']
        task_types = ['daily', 'weekly', 'monthly', 'temp', 'routine']
        type_map = {'daily':'日常走访','weekly':'每周走访','monthly':'月度回访','temp':'临时走访','routine':'常规走访'}
        for i in range(25):
            p = rand.choice(persons)
            st = rand.choice(statuses)
            tt = rand.choice(task_types)
            created = rdate(60)
            deadline = created + timedelta(days=rand.randint(1, 14))
            risk_label = '高风险' if p.risk_level == 'high' else '中风险' if p.risk_level == 'medium' else '低风险'
            task = VisitTask(
                person_id=p.person_id,
                title=f'【{risk_label}】{p.name}{type_map[tt]}',
                description=f'{p.name}的定期走访任务，等级{p.risk_level}，住址{p.address}',
                task_type=tt,
                assigned_to=1 if st != 'pending' else None,
                assigned_by=1,
                deadline=deadline,
                status=st,
                created_at=created,
            )
            db.session.add(task)
        db.session.commit()
        print('Visit tasks: 25 added')

    if VisitRecord.query.count() == 0:
        tasks = VisitTask.query.filter_by(status='completed').all()
        count = 0
        for task in tasks[:10]:
            vr = rdate(30)
            record = VisitRecord(
                task_id=task.task_id,
                person_id=task.person_id,
                visitor_id=1,
                visit_time=vr,
                location=task.person.address,
                longitude=119.1 + rand.random() * 0.3,
                latitude=31.2 + rand.random() * 0.2,
                content=f'对{task.person.name}进行走访，目前情况稳定。',
                performance=rand.choice(['良好','一般','良好','良好','较差']),
                thought_dynamics=rand.choice(['思想稳定','情绪平稳','略显焦虑','配合工作','抵触情绪']),
                life_difficulty=rand.choice(['无','经济困难','就业困难','家庭矛盾','住房困难']),
                has_abnormality=rand.random() < 0.2,
                abnormality_desc='发现异常行为，已上报' if rand.random() < 0.2 else None,
                photo_urls='[]',
            )
            db.session.add(record)
            count += 1
        db.session.commit()
        print(f'Visit records: {count} added')

    if RiskAssessment.query.count() <= 1:
        count = 0
        for p in persons:
            score = rand.randint(20, 95)
            level = 'high' if score >= 70 else 'medium' if score >= 40 else 'low'
            old_level = rand.choice(['low', 'medium', 'high'])
            details = {
                '人员类别': rand.randint(5, 25),
                '当前等级': {'low': 0, 'medium': 15, 'high': 30}[old_level],
                '暴力标签': 20 if rand.random() > 0.7 else 0,
                '无业': 10 if p.employment_status == '无业' else 0,
                '涉案': rand.randint(0, 15),
            }
            assessment = RiskAssessment(
                person_id=p.person_id, assessor_id=1,
                previous_risk_level=old_level, new_risk_level=level,
                score=score, score_details=details,
                reason='系统自动评估' if rand.random() > 0.3 else '人工调整',
                is_auto=rand.random() > 0.3, created_at=rdate(90),
            )
            db.session.add(assessment)
            count += 1
        db.session.commit()
        print(f'Risk assessments: {count} added')

    if Notification.query.count() <= 1:
        titles = [
            ('【系统通知】系统已完成升级维护', 'system'),
            ('【系统通知】请及时处理待办事项', 'system'),
            ('【预警通知】张强出现异常活动轨迹', 'alert'),
            ('【预警通知】刘洋复吸风险预警', 'alert'),
            ('【预警通知】马超脱离管控区域', 'alert'),
            ('【预警通知】宋涛近期频繁进京', 'alert'),
            ('【任务通知】您有新的走访任务待处理', 'task'),
            ('【任务通知】走访任务即将到期', 'task'),
            ('【任务通知】任务已完成，请确认结果', 'task'),
            ('【评估通知】张强风险等级已调整为高风险', 'assessment'),
            ('【评估通知】韩磊风险等级已调整为高风险', 'assessment'),
            ('【评估通知】人员批量评估已完成', 'assessment'),
            ('【评估通知】22人风险等级已更新', 'assessment'),
            ('【系统通知】请确认本月走访记录', 'system'),
            ('【系统通知】失联人员追踪进度更新', 'system'),
            ('【预警通知】何敏走失风险预警', 'alert'),
        ]
        for title, ntype in titles:
            days_ago = rand.randint(1, 30)
            notif = Notification(
                title=title, content=f'{title} - 请登录系统查看详情。',
                notification_type=ntype, sender_id=1, receiver_id=1,
                is_read=rand.random() < 0.4,
                read_at=datetime.now() - timedelta(days=rand.randint(0, days_ago)) if rand.random() < 0.4 else None,
                created_at=datetime.now() - timedelta(days=days_ago, hours=rand.randint(0, 23)),
            )
            db.session.add(notif)
        db.session.commit()
        print(f'Notifications: {len(titles)} added')

    if LostContactTrack.query.count() <= 1:
        lost_persons = [p for p in persons if p.risk_level == 'high'][:5]
        count = 0
        for p in lost_persons:
            lost_date = rdate(45)
            resolved = rand.random() > 0.5
            track = LostContactTrack(
                person_id=p.person_id, lost_time=lost_date,
                last_location=rand.choice([f'{p.address}附近', '火车站候车室', '长途汽车站', '城郊结合部']),
                search_measures=rand.choice(['已调取监控，正在排查', '已联系家属，发布协查通报', '已组织警力在周边搜寻']),
                family_contact=rand.choice(['父亲:13800138100', '母亲:13800138200', '配偶:13800138300']),
                progress=rand.choice(['正在排查监控视频', '已锁定最后出现区域', '已找到，正在带回']),
                status='resolved' if resolved else 'tracking',
                resolved_at=datetime.now() - timedelta(days=rand.randint(1, 10)) if resolved else None,
                created_at=lost_date,
            )
            db.session.add(track)
            count += 1
        db.session.commit()
        print(f'Lost contact tracks: {count} added')

    if PersonAlert.query.count() <= 1:
        atypes = ['行为异常', '脱管风险', '病情波动', '异常活动', '出入境预警', '复吸风险', '走失风险', '异常轨迹']
        levels = ['urgent', 'important', 'normal']
        statuses = ['pending', 'handled', 'dismissed']
        count = 0
        for i in range(12):
            p = rand.choice(persons)
            alert = PersonAlert(
                person_id=p.person_id,
                alert_type=rand.choice(atypes),
                alert_content=f'{p.name}出现{atypes[i % len(atypes)]}，需及时处理。当前等级{p.risk_level}',
                alert_level=rand.choice(levels),
                alert_time=datetime.now() - timedelta(days=rand.randint(1, 20), hours=rand.randint(0, 23)),
                status=rand.choice(statuses),
                handle_result='已核实处理' if rand.random() > 0.5 else None,
                handle_time=datetime.now() - timedelta(days=rand.randint(1, 5)) if rand.random() > 0.5 else None,
                handler_id=1 if rand.random() > 0.5 else None,
            )
            db.session.add(alert)
            count += 1
        db.session.commit()
        print(f'Person alerts: {count} added')

    print('Seed data complete!')
