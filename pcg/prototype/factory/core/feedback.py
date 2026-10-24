"""Unsigned human submissions are evidence to review, never auto-approval.

Only a deliberate curator decision can approve the experimental offline pool.
Test submissions cannot enter real stores, repair jobs or approval paths.
"""
import copy,json,re
from pathlib import Path
from .quality import digest

RATINGS=('fun','clarity','fairness','replay_value','difficulty')
FLAGS={'boring','unreadable_landing','unneeded_mechanic','excessive_wait','unexpected_shortcut','controls_issue'}
class FeedbackError(ValueError):pass

def check_catalog(catalog):
 if not isinstance(catalog,dict)or digest({k:v for k,v in catalog.items()if k!='catalog_sha256'})!=catalog.get('catalog_sha256'):raise FeedbackError('catalog_integrity')

def validate(submission,catalog,*,test_mode=False):
 check_catalog(catalog)
 if not isinstance(submission,dict)or submission.get('schema')!='pcg/human-feedback/v1':raise FeedbackError('feedback_schema')
 if submission.get('source_kind')not in ('human_self_report','synthetic_test'):raise FeedbackError('feedback_source_kind')
 if submission['source_kind']=='synthetic_test'and not test_mode:raise FeedbackError('synthetic_feedback_cannot_enter_real_store')
 if submission.get('catalog_sha256')!=catalog['catalog_sha256']:raise FeedbackError('stale_catalog')
 bindings={m['uid']:m['module_sha256']for m in catalog['review_modules']}
 uid=submission.get('candidate_uid')
 if uid not in bindings or submission.get('module_sha256')!=bindings[uid]:raise FeedbackError('unknown_or_stale_module')
 reviewer=submission.get('reviewer_code','')
 if not isinstance(reviewer,str)or not re.fullmatch(r'[A-Za-z0-9_-]{3,80}',reviewer):raise FeedbackError('reviewer_code')
 if submission.get('input_device')not in ('keyboard_mouse','gamepad','touch'):raise FeedbackError('input_device')
 for key in ('skill',)+RATINGS:
  v=submission.get(key)
  if type(v)is not int or not 1<=v<=5:raise FeedbackError('rating_'+key)
 flags=submission.get('flags',[])
 if not isinstance(flags,list)or len(flags)!=len(set(flags))or any(x not in FLAGS for x in flags):raise FeedbackError('feedback_flags')
 notes=submission.get('notes','')
 if not isinstance(notes,str)or len(notes)>2000:raise FeedbackError('feedback_notes')
 attempts=submission.get('manual_attempts')
 if not isinstance(attempts,list)or not attempts:raise FeedbackError('manual_attempt_required')
 for trial in attempts:
  if not isinstance(trial,dict)or trial.get('mode')!='manual'or trial.get('module_sha256')!=bindings[uid]:raise FeedbackError('replay_or_wrong_module_is_not_manual_play')
  if type(trial.get('frames'))is not int or trial['frames']<30:raise FeedbackError('manual_trial_too_short')
  if type(trial.get('input_events'))is not int or trial['input_events']<1:raise FeedbackError('manual_input_required')
 # Browser telemetry and reviewer code are client claims, not identity-proof.
 result=copy.deepcopy(submission);result['evidence_trust']='unsigned_client_self_report_requires_curator_confirmation';result['submission_sha256']=digest(submission)
 return result

def ingest(store_path,submissions,catalog,*,test_mode=False):
 path=Path(store_path)
 store=json.loads(path.read_text())if path.exists()else dict(schema='pcg/feedback-store/v1',catalog_sha256=catalog['catalog_sha256'],test_only=test_mode,submissions=[],decisions=[])
 if store['catalog_sha256']!=catalog['catalog_sha256']or store['test_only']!=test_mode:raise FeedbackError('store_scope_mismatch')
 accepted=[validate(x,catalog,test_mode=test_mode)for x in submissions]
 existing={s['submission_sha256']for s in store['submissions']}
 for s in accepted:
  if s['submission_sha256']not in existing:store['submissions'].append(s);existing.add(s['submission_sha256'])
 path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(store,ensure_ascii=False,indent=2));return store

def repair_job(store,catalog,*,diagnostic=False):
 check_catalog(catalog)
 if store.get('test_only')and not diagnostic:raise FeedbackError('test_store_cannot_drive_real_production')
 if diagnostic and not store.get('test_only'):raise FeedbackError('diagnostic_requires_explicit_test_store')
 if store['catalog_sha256']!=catalog['catalog_sha256']:raise FeedbackError('stale_feedback_store')
 tasks=[]
 for m in catalog['review_modules']:
  rows=[s for s in store['submissions']if s['candidate_uid']==m['uid']]
  flags=set(f for s in rows for f in s.get('flags',[]))
  if any(s['clarity']<=2 for s in rows):flags.add('unreadable_landing')
  if any(s['fun']<=2 for s in rows):flags.add('boring')
  for flag in sorted(flags):tasks.append(dict(candidate_uid=m['uid'],module_sha256=m['module_sha256'],target=flag,reviewers=sorted(set(s['reviewer_code']for s in rows)),source_submissions=[s['submission_sha256']for s in rows]))
 return dict(schema='pcg/factory-repair-job/v1',catalog_sha256=catalog['catalog_sha256'],test_only=bool(store.get('test_only')),source_kind='synthetic_test'if diagnostic else'human_self_report',tasks=tasks,scope='Revalidate every child; feedback never transfers approval to changed geometry.')

def decide(store,catalog,uid,decision,reviewer,reason,*,human_confirmed=False):
 check_catalog(catalog)
 if store['catalog_sha256']!=catalog['catalog_sha256']:raise FeedbackError('stale_feedback_store')
 if store.get('test_only'):raise FeedbackError('test_store_cannot_approve')
 if not human_confirmed:raise FeedbackError('explicit_human_curator_confirmation_required')
 if decision not in ('retain','rework','reject'):raise FeedbackError('decision')
 if not reviewer.strip()or not reason.strip():raise FeedbackError('curator_and_reason_required')
 rows=[s for s in store['submissions']if s['candidate_uid']==uid]
 candidates={c['uid']:c for c in catalog['candidates']}
 if uid not in candidates:raise FeedbackError('unknown_candidate')
 c=candidates[uid]
 if decision=='retain':
  if c['admission']['status']!='awaiting_human_review':raise FeedbackError('technical_gate_not_passed')
  if len(set(s['reviewer_code']for s in rows))<catalog['quality_policy']['minimum_human_reviewers']:raise FeedbackError('insufficient_distinct_human_reports')
 value=dict(candidate_uid=uid,decision=decision,curator=reviewer,reason=reason,source_submissions=[r['submission_sha256']for r in rows],human_curator_confirmation=True,approved_offline=decision=='retain',formal_game_ready=False)
 store['decisions'].append(value);return value
