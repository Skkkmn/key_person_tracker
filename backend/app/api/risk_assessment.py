from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.key_person import KeyPerson
from app.models.risk_assessment import RiskAssessment
from app.models.person_tag import Tag
from app.api.auth import login_required
from app.utils import log_operation

risk_bp = Blueprint('risk_assessment', __name__)


@risk_bp.route('/calculate/<int:person_id>', methods=['GET'])
@login_required
def calculate_risk(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    details, score = _calc_risk_score(person)

    level = 'low'
    if score >= 70:
        level = 'high'
    elif score >= 40:
        level = 'medium'

    return jsonify({
        'code': 200,
        'data': {
            'person_id': person_id,
            'person_name': person.name,
            'current_level': person.risk_level,
            'calculated_level': level,
            'score': score,
            'score_details': details,
        }
    })


@risk_bp.route('/apply/<int:person_id>', methods=['POST'])
@login_required
def apply_risk_assessment(person_id):
    person = KeyPerson.query.get(person_id)
    if not person:
        return jsonify({'code': 404, 'message': '人员不存在'}), 404

    data = request.get_json()
    new_level = data.get('risk_level', '')
    reason = data.get('reason', '')
    manual_score = data.get('score')
    manual_details = data.get('score_details')

    if new_level not in ('high', 'medium', 'low'):
        return jsonify({'code': 400, 'message': '无效的风险等级'}), 400

    previous = person.risk_level
    person.risk_level = new_level

    if manual_score is None:
        _, manual_score = _calc_risk_score(person)
    score = manual_score or 0

    assessment = RiskAssessment(
        person_id=person_id,
        assessor_id=request.current_user['user_id'],
        previous_risk_level=previous,
        new_risk_level=new_level,
        score=score,
        score_details=manual_details or _calc_risk_score(person)[0],
        reason=reason,
        is_auto=False,
    )
    db.session.add(assessment)
    db.session.commit()

    log_operation('APPLY_RISK', 'risk_assessment', assessment.assessment_id,
                  f'{person.name}: {previous}→{new_level}')
    return jsonify({'code': 200, 'message': '风险评估已应用', 'data': assessment.to_dict()})


@risk_bp.route('/history/<int:person_id>', methods=['GET'])
@login_required
def get_risk_history(person_id):
    assessments = RiskAssessment.query.filter_by(person_id=person_id)\
        .order_by(RiskAssessment.created_at.desc()).all()
    return jsonify({'code': 200, 'data': [a.to_dict() for a in assessments]})


@risk_bp.route('/auto-all', methods=['POST'])
@login_required
def auto_assess_all():
    persons = KeyPerson.query.all()
    results = []
    for p in persons:
        details, score = _calc_risk_score(p)
        level = 'low'
        if score >= 70:
            level = 'high'
        elif score >= 40:
            level = 'medium'

        previous = p.risk_level
        if level != previous:
            p.risk_level = level
            assessment = RiskAssessment(
                person_id=p.person_id,
                assessor_id=request.current_user['user_id'],
                previous_risk_level=previous,
                new_risk_level=level,
                score=score,
                score_details=details,
                reason='系统自动评估',
                is_auto=True,
            )
            db.session.add(assessment)
            results.append({'person_id': p.person_id, 'name': p.name, 'from': previous, 'to': level})

    db.session.commit()
    log_operation('AUTO_ASSESS', 'risk_assessment',
                  entity_name=f'自动评估完成，{len(results)}人等级发生变更')
    return jsonify({'code': 200, 'message': f'评估完成，{len(results)}人等级发生变更', 'data': results})


def _calc_risk_score(person):
    details = {}
    score = 0

    has_violence = any(t.tag_name in ('暴力倾向', '精神异常') for t in (person.tags or []))
    is_unemployed = person.employment_status in ('无业', '待业')
    is_lost = person.control_status in ('lost', 'missing')

    category_risk = {3: 20, 4: 15, 5: 25, 6: 20}
    cat_score = category_risk.get(person.category_id, 5)
    details['人员类别'] = cat_score
    score += cat_score

    risk_map = {'high': 30, 'medium': 15, 'low': 0}
    curr_risk = risk_map.get(person.risk_level, 5)
    details['当前等级'] = curr_risk
    score += curr_risk

    if has_violence:
        details['暴力/精神异常标签'] = 20
        score += 20

    if is_unemployed:
        details['无业/待业'] = 10
        score += 10

    if is_lost:
        details['失联状态'] = 25
        score += 25

    if person.case_description:
        case_len = len(person.case_description)
        case_score = min(case_len // 10, 15)
        if case_score > 0:
            details['涉案描述长度'] = case_score
            score += case_score

    score = min(score, 100)
    return details, score
