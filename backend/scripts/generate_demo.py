from datetime import datetime, timedelta, timezone
from pathlib import Path
import json

random_seed = 42


def ev(eid, sid, seq, typ, actor, content=None, tool_name=None, tool_input=None, tool_output=None):
    return {
        'event_id': eid,
        'session_id': sid,
        'sequence': seq,
        'timestamp': (datetime(2026, 9, 27, 7, 0, tzinfo=timezone.utc) + timedelta(seconds=seq)).isoformat(),
        'event_type': typ,
        'actor': actor,
        'content': content,
        'tool_name': tool_name,
        'tool_input': tool_input,
        'tool_output': tool_output,
        'metadata': {},
    }


def make(i, ft, domain):
    sid = f'SES-{i:04d}'
    oid = f'ORD-{20000+i:05d}'
    oid2 = f'ORD-{30000+i:05d}'
    cid = f'CUST-{1000+i:04d}'

    events = [ev(f'EVT-{i:03d}01', sid, 1, 'message', 'user', f'Please help with my {domain.lower()} request for {oid}.')]
    truth = {'status': 'success', 'failure_type': None}

    if ft == 'unsupported_success':
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'tool_call', 'agent', tool_name='cancel_order', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}03', sid, 3, 'tool_result', 'tool', tool_name='cancel_order', tool_output={'status': 'failed', 'order_id': oid, 'error': 'already shipped'}),
            ev(f'EVT-{i:03d}04', sid, 4, 'message', 'agent', 'Your order was successfully cancelled.'),
        ]
        truth = {'status': 'failure', 'failure_type': ft}
    elif ft == 'no_progress':
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'tool_call', 'agent', tool_name='track_shipment', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}03', sid, 3, 'tool_result', 'tool', tool_name='track_shipment', tool_output={'status': 'failed', 'order_id': oid, 'error': 'temporary'}),
            ev(f'EVT-{i:03d}04', sid, 4, 'tool_call', 'agent', tool_name='track_shipment', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}05', sid, 5, 'tool_result', 'tool', tool_name='track_shipment', tool_output={'status': 'failed', 'order_id': oid, 'error': 'temporary'}),
            ev(f'EVT-{i:03d}06', sid, 6, 'message', 'agent', 'I am still working on the request.'),
        ]
        truth = {'status': 'failure', 'failure_type': ft}
    elif ft == 'wrong_record':
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'tool_call', 'agent', tool_name='get_order', tool_input={'order_id': oid, 'customer_id': cid}),
            ev(f'EVT-{i:03d}03', sid, 3, 'tool_result', 'tool', tool_name='get_order', tool_output={'status': 'success', 'order_id': oid2, 'customer_id': cid}),
            ev(f'EVT-{i:03d}04', sid, 4, 'message', 'agent', 'I found your order and can continue.'),
        ]
        truth = {'status': 'failure', 'failure_type': ft}
    elif ft == 'repeated_question':
        q = 'What is the order number?'
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'message', 'agent', q),
            ev(f'EVT-{i:03d}03', sid, 3, 'message', 'user', oid),
            ev(f'EVT-{i:03d}04', sid, 4, 'message', 'agent', q),
            ev(f'EVT-{i:03d}05', sid, 5, 'message', 'user', oid),
        ]
        truth = {'status': 'failure', 'failure_type': ft}
    elif ft == 'incomplete_request':
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'message', 'agent', 'Please provide the payment reference before I can process this.'),
            ev(f'EVT-{i:03d}03', sid, 3, 'message', 'user', 'I do not have it.'),
            ev(f'EVT-{i:03d}04', sid, 4, 'message', 'agent', 'The refund is completed and successfully processed.'),
        ]
        truth = {'status': 'failure', 'failure_type': ft}
    elif ft == 'ambiguous':
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'tool_call', 'agent', tool_name='refund_order', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}03', sid, 3, 'tool_result', 'tool', tool_name='refund_order', tool_output={'status': 'pending', 'order_id': oid}),
            ev(f'EVT-{i:03d}04', sid, 4, 'message', 'agent', 'The refund is being processed; I cannot confirm final completion yet.'),
        ]
        truth = {'status': 'ambiguous', 'failure_type': None}
    elif ft == 'retry_success':
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'tool_call', 'agent', tool_name='get_order_status', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}03', sid, 3, 'tool_result', 'tool', tool_name='get_order_status', tool_output={'status': 'failed', 'order_id': oid}),
            ev(f'EVT-{i:03d}04', sid, 4, 'tool_call', 'agent', tool_name='get_order_status', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}05', sid, 5, 'tool_result', 'tool', tool_name='get_order_status', tool_output={'status': 'success', 'order_id': oid, 'state': 'shipped'}),
            ev(f'EVT-{i:03d}06', sid, 6, 'message', 'agent', 'I found the latest order status: shipped.'),
        ]
    else:
        events += [
            ev(f'EVT-{i:03d}02', sid, 2, 'tool_call', 'agent', tool_name='get_order_status', tool_input={'order_id': oid}),
            ev(f'EVT-{i:03d}03', sid, 3, 'tool_result', 'tool', tool_name='get_order_status', tool_output={'status': 'success', 'order_id': oid, 'state': 'shipped'}),
            ev(f'EVT-{i:03d}04', sid, 4, 'message', 'agent', 'Your order status is shipped.'),
        ]

    return {
        'session_id': sid,
        'agent_id': 'novacart-support-agent',
        'domain': domain,
        'started_at': '2026-09-27T07:00:00+00:00',
        'ended_at': '2026-09-27T07:00:10+00:00',
        'user_request': events[0]['content'],
        'final_response': events[-1].get('content'),
        'expected_outcome': ['Complete the requested workflow or clearly explain why it cannot be completed.'],
        'events': events,
        'ground_truth': truth,
    }


def generate():
    domains = ['Orders', 'Refunds', 'Returns', 'Shipping', 'Payments', 'Customer accounts', 'Address changes', 'Other']
    items = []
    for i in range(1, 101):
        if i <= 65:
            ft = 'success'
        elif i <= 72:
            ft = 'retry_success'
        elif i <= 80:
            ft = 'unsupported_success'
        elif i <= 86:
            ft = 'no_progress'
        elif i <= 91:
            ft = 'wrong_record'
        elif i <= 95:
            ft = 'repeated_question'
        elif i <= 98:
            ft = 'incomplete_request'
        else:
            ft = 'ambiguous'
        items.append(make(i, ft, domains[(i - 1) % len(domains)]))

    out = {
        'dataset_name': 'NovaCart Agent Reliability Demo',
        'dataset_version': '1.0',
        'description': 'Frozen 100-session synthetic dataset for AgentLens. Ground truth is evaluation-only.',
        'sessions': items,
    }
    data_dir = Path(__file__).resolve().parents[1].joinpath('data')
    data_dir.mkdir(parents=True, exist_ok=True)
    data_dir.joinpath('agentlens_demo.json').write_text(json.dumps(out, indent=2), encoding='utf-8')

    public = {
        'dataset_name': out['dataset_name'],
        'dataset_version': out['dataset_version'],
        'description': out['description'],
        'sessions': [{k: v for k, v in s.items() if k != 'ground_truth'} for s in items],
    }
    data_dir.joinpath('agentlens_demo_public.json').write_text(json.dumps(public, indent=2), encoding='utf-8')
    print(f'generated {len(items)} sessions')


if __name__ == '__main__':
    generate()
